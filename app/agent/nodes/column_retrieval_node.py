from langgraph.runtime import Runtime
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agent.llm import llm_model
from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.prompts.loader_prompt import load_prompt
from app.entities.entity import ColumnInfo
from app.common.logger import logger
from app.common.convert_to_qdrant_format import convert_single_to_qdrant

"""
字段召回节点
根据用户query关键词，从Qdrant检索相关字段
"""
async def retrieval_columns(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    step = "召回字段信息"
    writer({"type": "progress", "step": step, "status": "running"})

    try:
        keywords = state["keywords"]
        query = state["rewritten_query"]

        column_qdrant_repository = runtime.context["column_qdrant_repository"]
        embedding_client = runtime.context["embedding_client"]

        prompt = PromptTemplate(
            # 加载已经写好角色模板
            template= load_prompt("extend_keywords_for_column_recall"),
            input_variables=["query"]
        )

        # prompt要求只输出json格式
        json_parser = JsonOutputParser()
        # 生成一组用于字段召回的字段名列表。
        chain = prompt | llm_model | json_parser
        result = await chain.ainvoke(input={"query": query})

        # 原始关键词和 LLM 扩展词一起参与召回；set 去重，避免重复请求同一关键词
        keywords = set(keywords + result)

        # 用字段 id 做唯一键，因为多个关键词、同一字段的多个向量点都可能命中同一个字段
        column_info_map: dict[str, ColumnInfo] = {}
        for keyword in keywords:
            # 1. 获取特征向量 np.ndarray
            feature = await embedding_client.feature_extraction(keyword)
             # 2. 然后处理结果 np.ndarray--> list[float]
            keyword_vector = convert_single_to_qdrant(feature)
            result_column_infos: list[ColumnInfo] = await column_qdrant_repository.search(keyword_vector)
            for column_info in result_column_infos:
                if column_info.id not in column_info_map:
                    column_info_map[column_info.id] = column_info

        # 写回 state 的是去重后的 ColumnInfo 列表，不暴露 Qdrant 原始 point 结构
        retrieved_column_infos: list[ColumnInfo] = list(column_info_map.values())

        writer({"type": "progress", "step": step, "status": "success"})
        return {"retrieved_column_infos": retrieved_column_infos}

    except Exception as e:
        logger.error(f"{step} failed: {e}")
        writer({"type": "progress", "step": step, "status": "error"})
        raise


