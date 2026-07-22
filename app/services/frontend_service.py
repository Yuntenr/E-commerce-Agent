from app.repositories.mysql.user_repository import UserRepository
from app.entities.entity import UserInfo

class RegisterService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register(
        self,
        username: str,
        password: str,
        avatar: str | None = None
    ) -> UserInfo:

        # 1. 判断用户名是否存在
        exist: bool = await self.user_repository.exist_by_username(username)
        print("exist", exist, type(exist))
        if exist:
            raise Exception(f"用户名 '{username}' 已存在，请换一个")
        # 2. 创建用户
        user = await self.user_repository.create_user(
            username=username,
            password=password,
            avatar=avatar
        )
        return user

class LoginService:
    def __init__(self,user_repository: UserRepository):
        self.user_repository = user_repository

    async def login(self, username: str, password: str):
        # 1. 查询用户
        user: UserInfo = await self.user_repository.get_user_by_username(username)
        if user is None:
            raise Exception("用户不存在")
        # 2. 校验密码
        if user.password != password:
            raise Exception("密码错误")
        # 3. 返回用户信息
        return user