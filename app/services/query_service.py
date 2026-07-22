import json
from huggingface_hub import AsyncInferenceClient

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext

from app.agent.graph import graph
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw_repository import DwRepository
from app.repositories.mysql.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.repositories.redis.memory_redis_repository import MemoryRedisRepository


class QueryService:
    def __init__(self,
                 meta_mysql_repository: MetaMySQLRepository,
                 dw_repository: DwRepository,
                 metric_qdrant_repository: MetricQdrantRepository,
                 column_qdrant_repository: ColumnQdrantRepository,
                 value_es_repository: ValueESRepository,
                 embedding_client: AsyncInferenceClient,
                 memory_redis_repository: MemoryRedisRepository):
        
        # MySQL 仓储分别负责元数据补全和真实数仓环境信息读取
        self.meta_mysql_repository=meta_mysql_repository
        self.dw_repository=dw_repository

        # 召回链路依赖的向量检索、Embedding 和全文检索能力由依赖层注入
        self.metric_qdrant_repository=metric_qdrant_repository
        self.column_qdrant_repository=column_qdrant_repository
        self.value_es_repository=value_es_repository
        self.embedding_client = embedding_client
        self.memory_redis_repository=memory_redis_repository

    """执行一次问数工作流，并逐段产出 SSE 消息"""
    async def query(self, query: str, user_id: int, session_id: str | None):
        print("session_id", session_id)
        if session_id is None:
            session_id = await self.memory_redis_repository.create_session(user_id)
            yield ("data: " + json.dumps({"type":"session","session_id":session_id},ensure_ascii=False) + "\n\n"
        )
        session = await self.memory_redis_repository.get_session(session_id)

        # 1. 将用户问题以及历史消息传入state，初始化state
        state = DataAgentState(
            query=query,
            session_id=session_id,
            history=session["history"],
            )
        # 2. Context 保存本次图执行需要复用的外部依赖，节点通过 runtime.context 读取
        context = DataAgentContext(
            embedding_client=self.embedding_client,
            metric_qdrant_repository=self.metric_qdrant_repository,
            column_qdrant_repository=self.column_qdrant_repository,
            value_es_repository=self.value_es_repository,
            meta_mysql_repository=self.meta_mysql_repository,
            dw_mysql_repository=self.dw_repository,
            memory_redis_repository=self.memory_redis_repository
        )

        try:
            # stream_mode="custom" 使 graph.astream() 返回节点内部 runtime.stream_writer(...) 写出的自定义流消息
            async for chunk in graph.astream(
                input=state,
                context=context,
                stream_mode="custom"
            ):
                # 生成 SSE（Server-Sent Events）格式的数据
                # SSE 要求每条消息以 data: 开头，并以两个换行符结束
                yield("data:" + json.dumps(chunk, ensure_ascii=False, default=str) + "\n\n")
                     
        except Exception as e:
            # 流式接口已经开始返回后不能再改 HTTP 状态码，因此把异常也包装成一条 SSE 消息
            error = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(error, ensure_ascii=False, default=str)}\n\n"



