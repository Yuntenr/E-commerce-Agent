import argparse
import asyncio
from pathlib import Path

from app.client.mysql_client_manager import dw_mysql_client_manager, meta_mysql_client_manager
from app.client.qdrant_client_manager import qdrant_client_manager
from app.client.embedding_client_manager import embedding_client_manager
from app.client.es_client_manager import es_client_manager
from app.repositories.mysql.dw_repository import DwRepository
from app.repositories.mysql.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.es.value_es_repository import ValueESRepository
from app.services.meta_import_service import MetaDBService

async def build_meta_knowledge():

    # 初始化 Engine 和 Session 工厂
    dw_mysql_client_manager.init()
    meta_mysql_client_manager.init()

    qdrant_client_manager.init()
    embedding_client_manager.init()
    es_client_manager.init()

    async with (
        dw_mysql_client_manager.session_factory() as dw_session,
        meta_mysql_client_manager.session_factory() as meta_session
    ):
        dw_repository = DwRepository(dw_session)
        meta_repository = MetaMySQLRepository(meta_session)
        metric_qdrant_repository = MetricQdrantRepository(qdrant_client_manager.client)
        column_qdrant_repository = ColumnQdrantRepository(qdrant_client_manager.client)
        value_es_repository = ValueESRepository(es_client_manager.client)
        embedding_client = embedding_client_manager.client

        meta_db_sevice = MetaDBService(
            meta_mysql_repository=meta_repository,
            dw_repository=dw_repository,
            metric_qdrant_repository=metric_qdrant_repository,
            column_qdrant_repository=column_qdrant_repository,
            value_es_repository=value_es_repository,
            embedding_client=embedding_client
        )

        await meta_db_sevice.build()

    # 结束后关闭客户端连接
    await meta_mysql_client_manager.close()
    await dw_mysql_client_manager.close()
    # await qdrant_client_manager.close()
    # await es_client_manager.close()

if __name__ == "__main__":
    # 解析命令行参数，由外部决定本次构建使用哪份配置文件
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-c", "--conf", required=True)
    # args = parser.parse_args()

    # 将字符串路径转成 Path，再启动异步 build
    asyncio.run(build_meta_knowledge())
