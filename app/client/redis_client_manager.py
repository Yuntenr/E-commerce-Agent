import json
from redis.asyncio import Redis
from app.config.app_config import appconfig


class RedisClientManager:

    def __init__(self):
        self.client: Redis | None = None

    def init(self):
        if self.client is None:
            redis_config = appconfig.redis
            self.client = Redis(
                host=redis_config.host,
                port=redis_config.port,
                db=redis_config.db,
                password=redis_config.password,
                decode_responses=True,
                encoding="utf-8"
            )

    async def close(self):
        """
        关闭 Redis 连接
        """
        if self.client:
            await self.client.close()
            self.client = None

redis_client_manager = RedisClientManager()