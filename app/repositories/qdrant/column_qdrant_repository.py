from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client import AsyncQdrantClient
from app.entities.entity import ColumnInfo
from app.config.app_config import appconfig

class ColumnQdrantRepository:
    """负责字段向量集合的创建 写入和基础检索"""
    collection_name = "column_info_collection"
    def __init__(self, client: AsyncQdrantClient):
        self.client = client

    async def ensure_collection(self):
        if not await self.client.collection_exists(self.collection_name):
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=appconfig.qdrant.embedding_size,
                    distance=Distance.COSINE
                )
            )

    # Update + Insert（更新或插入）
    async def upsert(self,
                     ids: list[str],
                     vectors: list[list[float]],
                     payloads: list[dict],
                     batch_size: int = 10):
        
        points: list[PointStruct] = [
            PointStruct(
                id=id,
                vector=vector,
                payload=payload
            ) for id, vector, payload in zip(ids, vectors, payloads)
        ]
        # 将大量 PointStruct 数据切分成多个 batch，然后分批写入 Qdrant。
        for i in range(0, len(points), batch_size):
            await self.client.upsert(
                collection_name=self.collection_name,
                points=points[i : i + batch_size]
            )

    async def search(self, 
                     query_vector: list[float], 
                     score_threshold: float = 0.6, 
                     limit: int = 20) -> list[ColumnInfo]:
        # result: types.QueryResponse
        result = await self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            score_threshold=score_threshold,
            limit=limit
        )

        return [ColumnInfo(**point.payload) for point in result.points]

    async def delete(self, column_id: str):
        await self.client.delete(
            collection_name=self.collection_name,
            points_selector=[
                column_id
            ]
        )
        