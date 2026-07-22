import yaml

from langgraph.runtime import Runtime
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from app.common.logger import logger
from app.prompts.loader_prompt import load_prompt
from app.agent.llm import llm_model

"""基于已检索和过滤的上下文生成 SQL"""
async def sql_generator(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    step = "生成SQL"
    writer({"type": "progress", "step": step, "status": "running"})

    try:
        # 这些上下文都由前置节点准备完成，模型只在给定表 字段 指标口径范围内生成 SQL
        table_infos = state["table_infos"]
        metric_infos = state["metric_infos"]
        date_info = state["date_info"]
        db_info = state["db_info"]
        query = state["rewritten_query"]

        prompt = PromptTemplate(
            template=load_prompt("generate_sql"),
            input_variables=[
                "table_infos",
                "metric_infos",
                "date_info",
                "db_info",
                "query"
            ]
        )
        # SQL 生成节点只需要纯文本 SQL，不能要求模型输出 JSON 或 Markdown 代码块
        str_parser = StrOutputParser()
        chain = prompt | llm_model | str_parser
        # YAML 更适合放进提示词：保留嵌套结构 顺序和中文说明，方便模型理解表字段关系
        table_infos_to_yaml = yaml.dump(data=table_infos, allow_unicode=True, sort_keys=False)
        metric_infos_to_yaml = yaml.dump(data=metric_infos, allow_unicode=True, sort_keys=False)
        date_info_to_yaml = yaml.dump(data=date_info, allow_unicode=True, sort_keys=False)
        db_info_to_yaml = yaml.dump(data=db_info, allow_unicode=True, sort_keys=False)

        result = await chain.ainvoke(input={
            "table_infos": table_infos_to_yaml,
            "metric_infos": metric_infos_to_yaml,
            "date_info": date_info_to_yaml,
            "db_info": db_info_to_yaml,
            "query": query
        })
        
        logger.info(f"生成的SQL：{result}")
        writer({"type": "progress", "step": step, "status": "success"})
        return {"sql": result}
    
    except Exception as e:
        logger.error(f"{step} failed: {e}")
        writer({"type": "progress", "step": step, "status": "error"})
        raise
