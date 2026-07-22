from typing import TypedDict
from app.entities.entity import ColumnInfo, MetricInfo, ValueInfo

class DBInfoState(TypedDict):
    """SQL 生成阶段使用的数据库环境信息"""
    dialect: str
    version: str

class ColumnInfoState(TypedDict):
    """表上下文中的字段信息"""
    name: str
    type: str  # 数据类型int、varchar
    role: str  # 是否主键
    description: str
    alias: list[str]
    examples: list

class TableInfoState(TypedDict):
    """SQL 生成阶段真正传给模型的表结构上下文"""
    name: str
    type: str
    description: str
    columns: list[ColumnInfoState]

class MetricInfoState(TypedDict):
    """面向 SQL 生成提示词的指标信息"""
    name: str
    description: str
    relevant_columns: list[str]
    alias: list[str]

class DateInfoState(TypedDict):
    """SQL 生成阶段使用的当前日期上下文"""
    date: str
    weekday: str
    quater: str

class HistoryQA(TypedDict):
    question: str  
    result: str
    # 本轮产生的实体
    entities: list["ContextEntity"]
    # 当前轮次
    turn_id: int

class ContextEntity(TypedDict):
    # 实体类型
    # product / brand / region / metric / date
    type: str
    # 展示名称
    name: str
    # 来源
    # user_query / sql_result / rag / inference
    source: str


class DataAgentState(TypedDict):

    query:str  # 用户输入
    keywords: list[str]  # 抽取的关键词

    # 会话id
    session_id: str
    # 历史对话
    history: list[HistoryQA]
    # 上一个会话实体
    active_entities: list[ContextEntity]
    # Memory检索出的候选实体
    retrieved_memory_entities: list[ContextEntity]
    # 改写后的完整问题
    rewritten_query: str
    # 当前会话新产生的实体
    new_entities: list[ContextEntity]

    # RAG检索（召回）
    retrieved_column_infos: list[ColumnInfo]  # 检索到的字段信息
    retrieved_metric_infos: list[MetricInfo]  # 检索到的指标信息
    retrieved_value_infos: list[ValueInfo]  # 检索到的取值信息

    db_info: DBInfoState # 数据库语言和版本信息
    # RAG检索结果，Schema上下文
    table_infos: list[TableInfoState] # 合并和补齐后的表结构上下文
    metric_infos: list[MetricInfoState] # 合并后的指标上下文
    date_info: DateInfoState # 当前日期 星期和季度信息

    # SQL流程
    sql:str
    sql_error:str

    # 执行结果
    sql_result:list
