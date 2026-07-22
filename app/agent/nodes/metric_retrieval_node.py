from langgraph.runtime import Runtime
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from app.common.logger import logger
from app.prompts.loader_prompt import load_prompt
from app.agent.llm import llm_model
from app.entities.entity import MetricInfo
from app.common.convert_to_qdrant_format import convert_single_to_qdrant


async def retrieval_metric(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    step = "召回指标信息"
    writer({"type": "progress", "step": step, "status": "running"})

    try:
        keywords = state["keywords"]
        query = state["rewritten_query"]
        # 指标召回使用向量检索，需要 Embedding 客户端和指标 Qdrant 仓储配合
        embedding_client = runtime.context["embedding_client"]
        metric_qdrant_repository = runtime.context["metric_qdrant_repository"]

        prompt = PromptTemplate(
            template=load_prompt("extend_keywords_for_metric_recall"),
            input_variables=["query"]
        )
        json_parser = JsonOutputParser()
        chain = prompt | llm_model | json_parser
        result = await chain.ainvoke(input={"query": query})

        keywords = set(keywords + result)

        # 用指标 id 做唯一键，避免多个关键词命中同一个指标时重复写入 state
        metric_info_map: dict[str, MetricInfo] = {}
        for keyword in keywords:
            feature = await embedding_client.feature_extraction(keyword)
            keyword_vector = convert_single_to_qdrant(feature)
            result_metric_infos: list[MetricInfo] = await metric_qdrant_repository.search(keyword_vector)
            for metric_info in result_metric_infos:
                if metric_info.id not in metric_info_map:
                    metric_info_map[metric_info.id]=metric_info

        retrieved_metric_infos: list[MetricInfo] = list(metric_info_map.values())
        logger.info(f"检索到指标信息：{list(metric_info_map.keys())}")
        writer({"type": "progress", "step": step, "status": "success"})
        return {"retrieved_metric_infos": retrieved_metric_infos}

    except Exception as e:
        logger.error(f"{step} failed {e}")
        writer({"type": "progress", "step": step, "status": "error"})
        raise