from typing import TypedDict
from huggingface_hub import AsyncInferenceClient

from app.repositories.mysql.dw_repository import DwRepository
from app.repositories.mysql.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.redis.memory_redis_repository import MemoryRedisRepository

class DataAgentContext(TypedDict):
    """LangGraph Runtime 中传递的上下文对象"""

    # embedding模型
    embedding_client: AsyncInferenceClient

    # 向量数据库
    metric_qdrant_repository: MetricQdrantRepository
    column_qdrant_repository: ColumnQdrantRepository

    # 字段取值全文检索仓储，负责从 Elasticsearch 检索真实字段值
    value_es_repository: ValueESRepository

    # 元数据仓储，负责在召回结果合并时补齐字段 表 主外键等结构信息
    meta_mysql_repository: MetaMySQLRepository

    # 数仓仓储，负责在额外上下文补全时读取数据库方言 版本等执行环境信息
    dw_mysql_repository: DwRepository

    memory_redis_repository: MemoryRedisRepository