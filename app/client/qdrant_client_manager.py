import asyncio
import random
from typing import Optional
from qdrant_client import AsyncQdrantClient, models
from app.config.app_config import appconfig, QdrantConfig

class QdrantClientManager:
    """
    管理 Qdrant 向量数据库客户端
    """
    def __init__(self, config: QdrantConfig):
        self.client: Optional[AsyncQdrantClient] = None
        self.config = config

    def _get_url(self) -> str:
        return f"http://{self.config.host}:{self.config.port}"
    
    def init(self):
        self.client = AsyncQdrantClient(url=self._get_url())

    async def close(self):
        """关闭 Qdrant 客户端连接"""
        await self.client.close()

qdrant_client_manager = QdrantClientManager(appconfig.qdrant)

if __name__ == "__main__":
    # 先初始化客户端，后面的测试逻辑才能真正访问 Qdrant
    qdrant_client_manager.init()

    async def test():
        """执行一次集合创建、写入和查询，验证 Qdrant 接入链路"""
        client = qdrant_client_manager.client
        # 如果集合不存在，就先创建一个集合
        if not await client.collection_exists("my_collection"):
            await client.create_collection(
                collection_name="my_collection",
                vectors_config=models.VectorParams(
                    # 当前集合中的向量维度是 10
                    size=10,
                    # 使用余弦相似度作为距离计算方式
                    distance=models.Distance.COSINE,
                ),
            )

        # 向集合中写入 100 个随机 point
        # 每个 point 都有一个 id 和一个 10 维向量
        await client.upsert(
            collection_name="my_collection",
            points=[
                models.PointStruct(
                    id=i,
                    vector=[random.random() for _ in range(10)],
                )
                for i in range(100)
            ],
        )

        # 用一个随机生成的查询向量做相似度检索
        # limit=10 表示最多返回 10 条结果
        # score_threshold=0.8 表示只保留分数不低于 0.8 的结果
        res = await client.query_points(
            collection_name="my_collection",
            query=[random.random() for _ in range(10)],  # type: ignore
            limit=10,
            score_threshold=0.8,
        )

        print(res)

    asyncio.run(test())

