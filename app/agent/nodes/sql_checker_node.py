from langgraph.runtime import Runtime

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from app.common.logger import logger
from app.prompts.loader_prompt import load_prompt
from app.agent.llm import llm_model
from app.repositories.mysql.dw_repository import DwRepository

"""校验 SQL，并返回 error 字段控制后续条件分支"""
async def sql_checker(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    step = "校验SQL"
    writer({"type": "progress", "step": step, "status": "running"})

    try:
        sql = state["sql"]

        # SQL 可用性必须交给真实数仓判断，这里从运行时上下文取 DW Repository
        dw_mysql_repository: DwRepository = runtime.context["dw_mysql_repository"]
        try:
            await dw_mysql_repository.validate(sql)
            writer({"type": "progress", "step": step, "status": "success"})
            logger.info("SQL语法正确")
            return {"error": None}
        except Exception as e:
            # 不抛出异常中断图执行，而是把错误写入状态，供条件分支进入 correct_sql
            logger.info(f"SQL语法错误：{str(e)}")
            writer({"type": "progress", "step": step, "status": "success"})
            return {"error": str(e)}
    
    except Exception as e:
        logger.error(f"{step} failed: {e}")
        writer({"type": "progress", "step": step, "status": "error"})
        raise

