import json
import uuid
from typing import Any

from redis.asyncio import Redis
from dataclasses import asdict
from app.config.app_config import appconfig
from app.agent.state import HistoryQA, ContextEntity
from typing import TypedDict

class SessionData(TypedDict):
    user_id: int
    history: list[dict]
    active_entities: list[dict]
    all_entities: list[dict]

class MemoryRedisRepository:
    def __init__(self, redis_client: Redis):
        self.prefix = appconfig.redis.prefix
        self.expire = appconfig.redis.expire
        self.redis_client = redis_client

    def _build_key(self, session_id: str) -> str:
        return f"{self.prefix}:{session_id}"
    
    async def create_session(self, user_id:int):
        session_id = str(uuid.uuid4())
        data = {
            "user_id": user_id,
            "history": [],
            "active_entities": [],
            "all_entities":[]
        }

        await self.redis_client.set(
            self._build_key(session_id),
            json.dumps(data, ensure_ascii=False),
            ex=self.expire
        )
        return session_id


    async def get_session(self, session_id:str) -> SessionData  | None:
        data = await self.redis_client.get(self._build_key(session_id))
        if not data:
            return None
        return json.loads(data)
    
    async def update_session(self, session_id: str, data: SessionData):
        await self.redis_client.set(
            self._build_key(session_id),
            json.dumps(data, ensure_ascii=False),
            ex=self.expire
        )

    async def save_session(self, session_id: str, history: HistoryQA, new_entities: list[ContextEntity]):
        session = await self.get_session(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")
        
        # 1. 保存历史问答
        session["history"].append(history)
        # 2. 更新 active_entities
        session["active_entities"] = new_entities
        # 3. 合并 all_entities
        existing_entities = session["all_entities"]
        for entity in new_entities:
            exist = False
            for old in existing_entities:
                if old["type"] == entity["type"] and old["name"] == entity["name"]:
                    exist = True
                    break
            if not exist:
                existing_entities.append(entity)
        session["all_entities"] = existing_entities

        await self.update_session(session_id, session)