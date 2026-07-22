from langgraph.runtime import Runtime
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from app.common.logger import logger
from app.prompts.loader_prompt import load_prompt
from app.agent.llm import llm_model
from app.entities.entity import ValueInfo

"""召回和用户问题相关的字段取值"""
async def retrieval_value(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    step = "召回字段取值"
    writer({"type": "progress", "step": step, "status": "running"})

    try:
        # query 用于让 LLM 生成字段值层面的检索词，keywords 来自上游通用关键词抽取
        query = state["rewritten_query"]
        keywords = state["keywords"]
        # 字段取值更关注真实文本命中，因此这里走 Elasticsearch，而不是向量检索
        value_es_repository = runtime.context["value_es_repository"]
        # 用 LLM 把用户问法扩展成“可能出现在字段值里的词”
        # 例如“华北地区”可以补充出“华北”，避免 SQL 条件值和真实存储值不一致
        prompt = PromptTemplate(
            template=load_prompt("extend_keywords_for_value_recall"),
            input_variables=["query"],
        )
        json_parser = JsonOutputParser()
        chain = prompt | llm_model | json_parser
        result = await chain.ainvoke(input={"query": query})

        # 通用关键词和字段值扩展词一起检索 ES，尽量提高真实取值召回率
        keywords = set(keywords + result)

        # 用 ValueInfo.id 去重，避免多个关键词命中同一条字段值记录
        value_infos_map: dict[str, ValueInfo] = {}
        for keyword in keywords:
            current_value_infos: list[ValueInfo] = await value_es_repository.search(keyword)
            for current_value_info in current_value_infos:
                if current_value_info.id not in value_infos_map:
                    value_infos_map[current_value_info.id] = current_value_info

        # 写回 state 的是去重后的字段值实体，后续合并节点再决定如何组织上下文
        retrieved_value_infos: list[ValueInfo] = list(value_infos_map.values())
        logger.info(f"检索到字段取值：{list(value_infos_map.keys())}")
        writer({"type": "progress", "step": step, "status": "success"})
        return {"retrieved_value_infos": retrieved_value_infos}

    except Exception as e:
        logger.error(f"{step} failed: {e}")
        writer({"type": "progress", "step": step, "status": "error"})
        raise


   