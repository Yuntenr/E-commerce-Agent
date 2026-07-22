import yaml
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.state import DataAgentState, MetricInfoState
from app.agent.context import DataAgentContext
from app.common.logger import logger
from app.prompts.loader_prompt import load_prompt
from app.agent.llm import llm_model

"""根据用户问题裁剪候选指标上下文"""
async def filter_metric(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    step = "过滤指标信息"
    writer({"type": "progress", "step": step, "status": "running"})

    try:
        query = state["rewritten_query"]
        metric_infos: list[MetricInfoState] = state["metric_infos"]

        prompt = PromptTemplate(
            template=load_prompt("filter_metric_info"),
            input_variables=["query", "metric_infos"]
        )
        json_parser = JsonOutputParser()
        chain = prompt | llm_model | json_parser

        metric_infos_to_yaml = yaml.dump(data=metric_infos, allow_unicode=True, sort_keys=False)
        result = await chain.ainvoke(input={"query": query, "metric_infos": metric_infos_to_yaml})

        filtered_metric_infos: list[MetricInfoState] = []
        for metric_info in metric_infos:
            if metric_info["name"] in result:
                filtered_metric_infos.append(metric_info)

        logger.info(f"过滤后的指标信息：{[filtered_metric_info['name'] for filtered_metric_info in filtered_metric_infos]}")
        writer({"type": "progress", "step": step, "status": "success"})
        return {"metric_infos": filtered_metric_infos}
    
    except Exception as e:
        logger.error(f"{step} failed: {e}")
        writer({"type": "progress", "step": step, "status": "error"})
        raise
