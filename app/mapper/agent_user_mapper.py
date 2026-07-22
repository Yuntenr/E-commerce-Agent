from dataclasses import asdict
from app.entities.entity import UserInfo
from app.orm.agent_user_model import UserInfoMySQL


"""ColumnInfo Entity <-> ORM"""
class AgentUserMapper:
    def to_entity(user_info_mysql: UserInfoMySQL) -> UserInfo:
        return UserInfo(
            id=user_info_mysql.id,
            username=user_info_mysql.username,
            password=user_info_mysql.password,
        )
    
    def to_ormmodel(user_info: UserInfo) -> UserInfoMySQL:
        return UserInfoMySQL(**asdict(user_info))