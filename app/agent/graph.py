import asyncio

from langgraph.graph import StateGraph
from langgraph.constants import END, START
from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext

from app.agent.nodes.resolve_context_node import resolve_context_node
from app.agent.nodes.extract_keywords_node import extract_keywords_node
from app.agent.nodes.column_retrieval_node import retrieval_columns
from app.agent.nodes.metric_retrieval_node import retrieval_metric
from app.agent.nodes.value_retrieval_node import retrieval_value
from app.agent.nodes.merge_retrieval_info import merge_retrieval_info
from app.agent.nodes.filter_table import filter_table
from app.agent.nodes.filter_metric import filter_metric
from app.agent.nodes.add_extra_context import add_extra_context
from app.agent.nodes.sql_generator_node import sql_generator
from app.agent.nodes.sql_checker_node import sql_checker
from app.agent.nodes.sql_corrector_node import sql_corrector
from app.agent.nodes.sql_executor_node import sql_executor
from app.agent.nodes.entity_extract_node import extract_entities
from app.agent.nodes.save_memory_node import save_memory_node

from app.client.embedding_client_manager import embedding_client_manager
from app.client.qdrant_client_manager import qdrant_client_manager
from app.client.es_client_manager import es_client_manager
from app.client.mysql_client_manager import dw_mysql_client_manager, meta_mysql_client_manager
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw_repository import DwRepository
from app.repositories.mysql.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository

# StateGraph 声明整张图使用的状态结构和运行时上下文结构
graph_builder = StateGraph(state_schema=DataAgentState, context_schema=DataAgentContext)

# 注册节点
graph_builder.add_node("query_rewrite", resolve_context_node)
graph_builder.add_node("extract_keywords", extract_keywords_node)
graph_builder.add_node("retrieval_columns", retrieval_columns)
graph_builder.add_node("retrieval_metric", retrieval_metric)
graph_builder.add_node("retrieval_value", retrieval_value)
graph_builder.add_node("merge_retrieval_info", merge_retrieval_info)
graph_builder.add_node("filter_table", filter_table)
graph_builder.add_node("filter_metric", filter_metric)
graph_builder.add_node("add_extra_context", add_extra_context)
graph_builder.add_node("sql_generator", sql_generator)
graph_builder.add_node("sql_checker", sql_checker)
graph_builder.add_node("sql_corrector", sql_corrector)
graph_builder.add_node("sql_executor", sql_executor)
graph_builder.add_node("extract_entities", extract_entities)
graph_builder.add_node("save_memory", save_memory_node)

# 判断是否需要对问题进行改写
graph_builder.add_edge(START, "query_rewrite")

# 从用户问题开始，先抽取关键词作为后续检索的基础
graph_builder.add_edge("query_rewrite", "extract_keywords")

# 抽取关键词后，通过rag检索召回三类（字段、指标、字段真实值）字段
graph_builder.add_edge("extract_keywords", "retrieval_columns")
graph_builder.add_edge("extract_keywords", "retrieval_metric")
graph_builder.add_edge("extract_keywords", "retrieval_value")

# 召回三类字段后，统一送到 信息合并节点
graph_builder.add_edge("retrieval_columns", "merge_retrieval_info")
graph_builder.add_edge("retrieval_metric", "merge_retrieval_info")
graph_builder.add_edge("retrieval_value", "merge_retrieval_info")

# 信息合并后，过滤表和指标中信息
graph_builder.add_edge("merge_retrieval_info", "filter_table")
graph_builder.add_edge("merge_retrieval_info", "filter_metric")

# 过滤后，补充额外所需的上下文
graph_builder.add_edge("filter_table", "add_extra_context")
graph_builder.add_edge("filter_metric", "add_extra_context")

# 生成sql
graph_builder.add_edge("add_extra_context", "sql_generator")

# 检查sql
graph_builder.add_edge("sql_generator", "sql_checker")

# 如果检查有错，进行纠正；检查没有错误直接执行sql
graph_builder.add_conditional_edges(
    source="sql_checker",
    path=lambda state: "sql_executor" if state["error"] is None else "sql_corrector",
    path_map={"sql_executor": "sql_executor", "sql_corrector": "sql_corrector"},
)

# 纠正后，执行sql
graph_builder.add_edge("sql_corrector", "sql_executor")

# SQL执行后,抽取实体
graph_builder.add_edge("sql_executor", "extract_entities")

# 抽取实体后保存Memory
graph_builder.add_edge("extract_entities", "save_memory")

# 终止
graph_builder.add_edge("save_memory", END)

# 编译后的 graph 是对外使用的 Agent 执行入口
graph = graph_builder.compile()


if __name__ == "__main__":

    async def test():
        """本地调试关键词抽取和字段 指标 取值三路召回链路"""

        # 多路召回和上下文补全会访问 Qdrant、Embedding、ES、Meta MySQL 和 DW MySQL
        qdrant_client_manager.init()
        embedding_client_manager.init()
        es_client_manager.init()
        meta_mysql_client_manager.init()
        dw_mysql_client_manager.init()

        # Meta MySQL 用来补齐元数据，DW MySQL 用来读取数据库方言和版本
        async with (
            meta_mysql_client_manager.session_factory() as meta_session,
            dw_mysql_client_manager.session_factory() as dw_session,
        ):
            meta_mysql_repository = MetaMySQLRepository(meta_session)
            dw_mysql_repository = DwRepository(dw_session)

            # 字段和指标分别使用不同 Qdrant collection，取值检索使用 ES index
            column_qdrant_repository = ColumnQdrantRepository(
                qdrant_client_manager.client
            )
            metric_qdrant_repository = MetricQdrantRepository(
                qdrant_client_manager.client
            )
            value_es_repository = ValueESRepository(es_client_manager.client)

            # 当前只需要传入原始问题，后续节点会逐步写回召回、过滤和额外上下文结果
            state = DataAgentState(query="统计华北地区的销售总额")
            context = DataAgentContext(
                column_qdrant_repository=column_qdrant_repository,
                embedding_client=embedding_client_manager.client,
                metric_qdrant_repository=metric_qdrant_repository,
                value_es_repository=value_es_repository,
                meta_mysql_repository=meta_mysql_repository,
                dw_mysql_repository=dw_mysql_repository,
            )

            # stream_mode="custom" 会接收各节点通过 runtime.stream_writer 写出的进度信息
            async for chunk in graph.astream(
                input=state, context=context, stream_mode="custom"
            ):
                print(chunk)

        # 关闭显式创建的异步客户端，避免本地调试时连接资源悬挂
        await qdrant_client_manager.close()
        await es_client_manager.close()
        await meta_mysql_client_manager.close()
        await dw_mysql_client_manager.close()

    asyncio.run(test())