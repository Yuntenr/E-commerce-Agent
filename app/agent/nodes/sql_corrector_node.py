import yaml

from langgraph.runtime import Runtime
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from app.common.logger import logger
from app.prompts.loader_prompt import load_prompt
from app.agent.llm import llm_model

"""根据校验错误修正 SQL"""
async def sql_corrector(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    step = "校正SQL"
    writer({"type": "progress", "step": step, "status": "running"})

    try:
        # 校正 SQL 仍然需要完整上下文，避免模型只根据报错修语法却改丢业务语义
        table_infos = state["table_infos"]
        metric_infos = state["metric_infos"]
        date_info = state["date_info"]
        db_info = state["db_info"]
        query = state["rewritten_query"]

        # sql 是待修正的候选 SQL，error 是数据库 explain 返回的具体错误信息
        sql = state["sql"]
        error = state["error"]
        
        prompt = PromptTemplate(
            template=load_prompt("correct_sql"),
            input_variables=[
                "table_infos",
                "metric_infos",
                "date_info",
                "db_info",
                "query",
                "sql",
                "error"
            ],
        )

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
            "query": query,
            "sql": sql,
            "error": error
        })
        
        logger.info(f"校正后的SQL{result}")
        writer({"type": "progress", "step": step, "status": "success"})
        return {"sql": result}
    
    except Exception as e:
        logger.error(f"{step} failed: {e}")
        writer({"type": "progress", "step": step, "status": "error"})
        raise

