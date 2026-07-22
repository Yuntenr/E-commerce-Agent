from app.orm.base import Base
from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

class ColumnMetricMySQL(Base):

    __tablename__ = "column_metric"

    # 这里采用联合主键
    # 表示同一对 字段 指标 关系只允许出现一次
    column_id: Mapped[str] = mapped_column(
        String(128),
        primary_key=True,
        comment="字段编号"
    )

    metric_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        comment="指标编号"
    )


# class ValueInfoMySQL(Base):
#     """value_info"""

#     __tablename__ = "value_info"

#     id: Mapped[str] = mapped_column(
#         String(128),
#         primary_key=True,
#         comment="取值编号"
#     )

#     value: Mapped[str] = mapped_column(
#         String(256),
#         comment="字段取值"
#     )

#     column_id: Mapped[str] = mapped_column(
#         String(128),
#         index=True,
#         comment="所属字段编号"
#     )