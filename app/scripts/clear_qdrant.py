import asyncio

from qdrant_client import AsyncQdrantClient
from app.client.qdrant_client_manager import qdrant_client_manager

from app.config.app_config import appconfig


# 需要清理的 collection
COLLECTIONS = [
    "column_info_collection",
    "metric_info_collection",
]


async def clear_qdrant():

    qdrant_client_manager.init()
    client = qdrant_client_manager.client

    print("开始清理 Qdrant...")

    for collection_name in COLLECTIONS:

        exists = await client.collection_exists(
            collection_name=collection_name
        )

        if exists:
            await client.delete_collection(
                collection_name=collection_name
            )

            print(
                f"✅ 删除 collection: {collection_name}"
            )

        else:
            print(
                f"⚠️ collection 不存在: {collection_name}"
            )

    await client.close()

    print("\nQdrant 清理完成")


if __name__ == "__main__":
    asyncio.run(clear_qdrant())