import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from app.config.app_config import appconfig, DBConfig

class MysqlClientManager:
    def __init__(self, config: DBConfig):
        self.engine: AsyncEngine | None = None
        self.session_factory = None
        self.config = config

    def get_url(self) -> str:
        url = f"mysql+asyncmy://{self.config.user}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}?charset=utf8mb4"
        # print("="*20, url)
        return url
    
    def init(self):
        """初始化 Engine 和 Session 工厂"""
        # 创建异步 Engine，相当于先把“数据库连接能力”准备好
        self.engine = create_async_engine(
            url=self.get_url(), pool_size=10, pool_pre_ping=True
        )
        # 基于 Engine 创建 Session 工厂，后面真正查库时再拿 session
        self.session_factory = async_sessionmaker(
            self.engine, autoflush=True, expire_on_commit=False
        )
    async def close(self):
        """释放连接池资源"""
        await self.engine.dispose()

# 一套连元数据库，一套连数仓模拟库
# 后续由不同 repository 按职责分别使用
meta_mysql_client_manager = MysqlClientManager(appconfig.meta_db)
dw_mysql_client_manager = MysqlClientManager(appconfig.dw_db)
user_mysql_client_manager = MysqlClientManager(appconfig.user_db)

if __name__ == "__main__":
    dw_mysql_client_manager.init()

    async def test():
        """执行一次简单查询，验证 MySQL 连接与结果结构"""
        async with dw_mysql_client_manager.session_factory() as session:
            sql = "select * from fact_order limit 5 "
            result = await session.execute(text(sql))
            # mappings().fetchall() 会把结果转成“按列名访问”的行对象列表
            rows = result.mappings().fetchall()
            print(type(rows))
            print(type(rows[0]))
            print(rows[0]["order_id"])

    asyncio.run(test())
      
