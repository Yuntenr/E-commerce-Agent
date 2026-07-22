import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.orm.agent_user_model import UserInfoMySQL
from app.entities.entity import UserInfo
from app.mapper.agent_user_mapper import AgentUserMapper

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, username: str, password: str, avatar: str | None = None) -> UserInfo:
            user = UserInfoMySQL(
                username=username,
                password=password,
                avatar=avatar
            )
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return AgentUserMapper.to_entity(user)
        
    async def exist_by_username(self, username:str) -> bool:
        sql = text(f"select id from agent_user where username = '{username}' limit 1")
        orm = await self.session.execute(sql)
        row = orm.fetchone()
        if row is None:
             return False
        else:
             return True
        
    async def get_user_by_username(self, username:str) -> UserInfo:
        sql = text(f"select * from agent_user where username = '{username}' limit 1")
        orm = await self.session.execute(sql)
        row = orm.fetchone()
        return AgentUserMapper.to_entity(row)
    
    async def exsit_user(self, username: str, password: str) -> bool:
        sql = text(f"select * from agent_user where username = '{username}' and User.password == `{password}`")
        result = await self.session.execute(sql)
        row = result.fetchone()
        if row is None:
             return False
        else:
             return True
