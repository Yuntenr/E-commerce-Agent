import yaml

from langgraph.runtime import Runtime
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from app.common.logger import logger
from app.prompts.loader_prompt import load_prompt
from app.agent.llm import llm_model
from app.repositories.mysql.dw_repository import DwRepository

"""执行 SQL 并产出最终问数结果"""
async def sql_executor(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    step = "执行SQL"
    writer({"type": "progress", "step": step, "status": "running"})

    try:
        # 这里拿到的可能是 sql_generator 直接通过校验的 SQL，也可能是 sql_corrector 覆盖后的 SQL
        sql = state["sql"]
        dw_mysql_repository = runtime.context["dw_mysql_repository"]

        result = await dw_mysql_repository.run(sql)
        logger.info(f"SQL执行结果：{result}")
        writer({"type": "progress", "step": step, "status": "success"})
        writer({"type": "result", "data": result})
        return {"sql_result": result}
    
    except Exception as e:
        logger.error(f"{step} failed: {e}")
        writer({"type": "progress", "step": step, "status": "error"})
        raise