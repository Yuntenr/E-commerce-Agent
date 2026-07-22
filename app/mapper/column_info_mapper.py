from dataclasses import asdict
from app.entities.entity import ColumnInfo
from app.orm.column_info_model import ColumnInfoMySQL

"""ColumnInfo Entity <-> ORM"""
class ColumnInfoMapper:
    def to_entity(column_info_mysql: ColumnInfoMySQL) -> ColumnInfo:
        return ColumnInfo(
            id=column_info_mysql.id,
            table_id=column_info_mysql.table_id,
            column_name=column_info_mysql.column_name,
            type=column_info_mysql.type,
            description=column_info_mysql.description,
            alias=column_info_mysql.alias,
            role=column_info_mysql.role,
            examples=column_info_mysql.examples
        )
    
    def to_ormmodel(column_info: ColumnInfo) -> ColumnInfoMySQL:
        return ColumnInfoMySQL(**asdict(column_info))
