import json
from decimal import Decimal
from datetime import datetime, date

from langgraph.runtime import Runtime
from langchain_core.output_parsers import StrOutputParser

from app.agent.state import DataAgentState, HistoryQA
from app.agent.context import DataAgentContext
from app.repositories.redis.memory_redis_repository import MemoryRedisRepository

from app.common.logger import logger

class CustomJSONEncoder(json.JSONEncoder):
    """自定义JSON编码器，处理数据库返回的特殊类型"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)  # 或 return str(obj) 保留精度
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, set):
            return list(obj)
        # 处理其他可能的类型
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

async def save_memory_node(state: DataAgentState, runtime: Runtime[DataAgentContext]):

    step = "保存会话记忆"
    writer = runtime.stream_writer
    writer({"type": "progress","step": step, "status": "running"})


    try:
        session_id = state["session_id"]
        history = state.get("history", []).copy()
        # 本轮新增实体
        new_entities = state.get("new_entities",[])

        # ✅ 使用自定义编码器序列化 SQL 结果
        answer = json.dumps(state["sql_result"], cls=CustomJSONEncoder, ensure_ascii=False)
        new_history=HistoryQA(
            question=state["query"],
            result=answer,
            entities=new_entities,
            turn_id=len(history) + 1
        )
        # 加入历史
        history.append(new_history)

        await runtime.context["memory_redis_repository"].save_session(
            session_id=session_id,
            history=history,
            new_entities=new_entities
        )
        writer({"type":"progress", "step":step, "status":"success"})
        logger.info("会话记忆保存成功")
        return {"history": history}

    except Exception as e:
        logger.error(f"保存记忆失败:{e}")
        writer({"type": "progress","step": step,"status": "error"})
        raise