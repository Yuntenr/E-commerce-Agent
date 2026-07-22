from app.orm.base import Base
from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

class ColumnInfoMySQL(Base):

    __tablename__ = "column_info"

    id: Mapped[str] = mapped_column(
        String(128),
        primary_key=True,
        comment="列编号(table.column)"
    )

    table_id: Mapped[str] = mapped_column(
        String(64),
        index=True,
        comment="所属表编号"
    )

    column_name: Mapped[str] = mapped_column(
        String(128),
        comment="字段名称"
    )

    type: Mapped[str] = mapped_column(
        String(64),
        comment="字段数据类型"
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        comment="字段描述"
    )

    alias: Mapped[list | None] = mapped_column(
        JSON,
        comment="字段别名"
    )

    role: Mapped[str] = mapped_column(
        String(32),
        comment="字段角色(primary_key/foreign_key/dimension/measure)"
    )

    examples: Mapped[dict | list | None] = mapped_column(
        JSON, 
        comment="数据示例"
    )
    