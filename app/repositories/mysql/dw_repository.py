import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.client.mysql_client_manager import dw_mysql_client_manager

class DwRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # 查询业务表中所有字段的数据类型。
    async def _get_column_type(self, table_name: str) -> dict[str: str]:
        sql = text(f"show columns from `{table_name}`")
        result = await self.session.execute(sql)
        column_types = {}
        for row in result:
            column_types[row.Field] = row.Type
        return column_types
    
    async def get_column_values(
        self, table_name: str, column_name: str, limit: int = 10
    ) -> list:
        """抽样查询字段示例值，供元数据入库和后续检索链路复用"""
        sql = f"select distinct {column_name} from {table_name} limit {limit}"
        result = await self.session.execute(text(sql))
        return [row[0] for row in result.fetchall()]

    async def get_db_info(self):
        """读取当前数仓数据库的方言和版本，供 SQL 生成提示词使用"""

        sql = "select version()"
        result = await self.session.execute(text(sql))
        version = result.scalar()

        # dialect 来自 SQLAlchemy 当前绑定的数据库方言，例如 mysql
        dialect = self.session.bind.dialect.name
        return {"dialect": dialect, "version": version}

    async def validate(self, sql: str):
        """用 EXPLAIN 让数据库提前解析 SQL，发现语法 表名 字段名等错误"""
        sql = f"explain {sql}"
        await self.session.execute(text(sql))

    async def run(self, sql: str) -> list[dict]:
        """执行最终 SQL，并把 SQLAlchemy 行对象转换成前端更易消费的字典列表"""
        result = await self.session.execute(text(sql))
        return [dict(row) for row in result.mappings().fetchall()]


"""for test"""
if __name__ == "__main__":
    dw_mysql_client_manager.init()
    async def test():
        async with dw_mysql_client_manager.session_factory() as dw_session:
            dw_repository = DwRepository(dw_session)

            column_types = await dw_repository._get_column_type("fact_order")
            print(column_types)
            print(type(column_types))
            print(column_types["order_id"])

    asyncio.run(test())