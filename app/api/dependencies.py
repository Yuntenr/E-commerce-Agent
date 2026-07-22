
from typing import Annotated
from huggingface_hub import AsyncInferenceClient
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from elasticsearch import AsyncElasticsearch
from qdrant_client import AsyncQdrantClient
from redis.asyncio import Redis

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from app.services.query_service import QueryService
from app.services.frontend_service import RegisterService, LoginService

from app.agent.graph import graph
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw_repository import DwRepository
from app.repositories.mysql.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.repositories.mysql.user_repository import UserRepository
from app.repositories.redis.memory_redis_repository import MemoryRedisRepository
from app.client.mysql_client_manager import meta_mysql_client_manager, dw_mysql_client_manager, user_mysql_client_manager
from app.client.es_client_manager import es_client_manager
from app.client.embedding_client_manager import embedding_client_manager
from app.client.qdrant_client_manager import qdrant_client_manager
from app.client.redis_client_manager import redis_client_manager

"""0. get_user_mysql_repository"""
async def get_user_session():
    async with user_mysql_client_manager.session_factory() as user_session:
        yield user_session

async def get_user_mysql_repository(session: Annotated[AsyncSession, Depends(get_user_session)]) -> UserRepository:

    user_mysql_repository = UserRepository(session=session)
    return user_mysql_repository

"""1. get_meta_mysql_repository"""
async def get_meta_session():
    """创建一次请求内使用的元数据库 Session"""
    # yield 之后的清理逻辑由 async with 负责，FastAPI 会在请求结束后继续执行退出流程
    async with meta_mysql_client_manager.session_factory() as meta_session:
        yield meta_session

async def get_meta_mysql_repository(session: Annotated[AsyncSession, Depends(get_meta_session)]) -> MetaMySQLRepository:

    meta_mysql_repository = MetaMySQLRepository(session=session)
    return meta_mysql_repository

"""2. get_dw_mysql_repository"""
async def get_dw_session():
    async with dw_mysql_client_manager.session_factory() as dw_session:
        yield dw_session

async def get_dw_mysql_repository(session: Annotated[AsyncSession, Depends(get_dw_session)]) -> DwRepository:

    return DwRepository(session) 

"""3. get_embedding_client"""
async def get_embedding_client() -> AsyncInferenceClient:
    
    return  embedding_client_manager.client

"""4. get_value_es_repository"""
async def get_value_es_repository() -> ValueESRepository:

    return ValueESRepository(es_client_manager.client)

"""5. get_column_qdrant_repository"""
async def get_column_qdrant_repository() -> ColumnQdrantRepository:

    return ColumnQdrantRepository(qdrant_client_manager.client)

"""6. get_metric_qdrant_repository"""
async def get_metric_qdrant_repository() -> MetricQdrantRepository:

    return MetricQdrantRepository(qdrant_client_manager.client)

"""7. get_memory_redis_repository"""
async def get_memory_redis_repository() -> MemoryRedisRepository:

    return MemoryRedisRepository(redis_client_manager.client)




"""组装一次查询所需的业务服务"""
async def get_query_service(
        meta_mysql_repository: Annotated[MetaMySQLRepository, Depends(get_meta_mysql_repository)],
        dw_repository: Annotated[DwRepository, Depends(get_dw_mysql_repository)],
        metric_qdrant_repository: Annotated[MetricQdrantRepository, Depends(get_metric_qdrant_repository)],
        column_qdrant_repository: Annotated[ColumnQdrantRepository, Depends(get_column_qdrant_repository)],
        value_es_repository: Annotated[ValueESRepository, Depends(get_value_es_repository)],
        embedding_client: Annotated[AsyncInferenceClient, Depends(get_embedding_client)],
        memory_redis_repository: Annotated[Redis, Depends(get_memory_redis_repository)]
        ) -> QueryService:
    
    # QueryService 只接收已经创建好的依赖对象，本身不关心这些对象来自 MySQL、Qdrant 还是 ES
    query_service = QueryService(
        meta_mysql_repository=meta_mysql_repository,
        dw_repository=dw_repository,
        metric_qdrant_repository=metric_qdrant_repository,
        column_qdrant_repository=column_qdrant_repository,
        value_es_repository=value_es_repository,
        embedding_client=embedding_client,
        memory_redis_repository=memory_redis_repository
    )
    return query_service

async def get_login_service(
        user_repository: Annotated[UserRepository, Depends(get_user_mysql_repository)]
) -> LoginService:
    login_service = LoginService(user_repository=user_repository)
    return login_service

async def get_register_service(
        user_repository: Annotated[UserRepository, Depends(get_user_mysql_repository)]
) -> RegisterService:
    register_service = RegisterService(user_repository=user_repository)
    return register_service