from dataclasses import dataclass
from typing import Any
from datetime import datetime

""" meta数据库中表所对应的实体类 """
@dataclass
class TableInfo:  # meata_table
    id: str
    name: str
    type: str  # 表类型 fact/dim
    description: str

@dataclass
class ColumnInfo:  # meta_columns
    id: str
    table_id: str
    column_name: str
    type: str  # 字段类型
    description: str
    alias: list[str]
    role: str  # 是否主键
    examples: list[Any]

@dataclass
class MetricInfo:  # metric_info
    id: str
    name: str
    description: str
    relevant_columns: list[str]
    alias: list[str]

@dataclass
class ColumnMetric:  # column_metric
    column_id: str
    metric_id: str

"""字段具体取值及其所属字段的业务表达,关联ColumnInfo"""
@dataclass
class ValueInfo:
    id: str
    value: str
    column_id: str

@dataclass
class UserInfo:
    id: int
    username: str
    password: str
    avatar: str | None = None