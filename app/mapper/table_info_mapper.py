from dataclasses import asdict

from app.entities.entity import TableInfo
from app.orm.table_info_model import TableInfoMySQL

"""meta_db数据库中meta_table表"""
class TableInfoMapper:

    """将ORM对象映射为entity实体"""
    @staticmethod
    def to_entity(table_info_mysql: TableInfoMySQL) -> TableInfo:
        return TableInfo(
            id=table_info_mysql.id,
            name=table_info_mysql.name,
            type=table_info_mysql.type,
            description=table_info_mysql.description
        )
    
    """将entity实体映射为ORM模型对象，交给 SQLAlchemy 托管"""
    @staticmethod
    def to_ormmodel(table_info: TableInfo) -> TableInfoMySQL:
        return TableInfoMySQL(**asdict(table_info))