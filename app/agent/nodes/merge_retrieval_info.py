from langgraph.runtime import Runtime
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from app.common.logger import logger
from app.prompts.loader_prompt import load_prompt
from app.agent.llm import llm_model
from app.entities.entity import ValueInfo, ColumnInfo, MetricInfo, TableInfo
from app.agent.state import TableInfoState, ColumnInfoState, MetricInfoState

"""合并召回结果，并输出 SQL 生成前的候选表信息和指标信息"""
async def merge_retrieval_info(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    step = "合并召回信息"
    writer({"type": "progress", "step": step, "status": "running"})

    try:
        # 1. 获取召回结果
        retrieved_column_infos: list[ColumnInfo] = state["retrieved_column_infos"]
        retrieved_metric_infos: list[MetricInfo] = state["retrieved_metric_infos"]
        retrieved_value_infos: list[ValueInfo] = state["retrieved_value_infos"]
        
        meta_mysql_repository = runtime.context["meta_mysql_repository"]

        # 2. 补齐metric_info中的相关字段
        # 以 column_id 为 key 合并字段信息，【column_info.id：ColumnInfo】 
        retrieved_column_infos_map: dict[str, ColumnInfo] = {
            retrieved_column_info.id: retrieved_column_info for retrieved_column_info in retrieved_column_infos
        }
        # 可能指标信息中相关字段没有被字段召回（retrieval column阶段）命中，就从 Meta MySQL 里按 id 查出来补进上下文。
        for retrieved_metric_info in retrieved_metric_infos:
            for relevant_column in retrieved_metric_info.relevant_columns:
                if relevant_column not in retrieved_column_infos_map:
                    column_info: ColumnInfo = await meta_mysql_repository.get_column(relevant_column)
                    retrieved_column_infos_map[relevant_column] = column_info

        # 3. 把字段取值合并回字段 examples
        # ValueInfo.id: {column_info.id}.{current_column_value} 如：{dim_region.region_name}.{华北}
        # 把真实 value 放进字段 examples，可以帮助模型写出更接近真实数据的 where 条件。
        for retrieved_value_info in retrieved_value_infos:
            value = retrieved_value_info.value
            column_id = retrieved_value_info.column_id
            if column_id not in retrieved_column_infos_map:
                column_info: ColumnInfo = await meta_mysql_repository.get_column(column_id)
                retrieved_column_infos_map[column_id] = column_info

            if value not in retrieved_column_infos_map[column_id].examples:
                retrieved_column_infos_map[column_id].examples.append(value)

        # 4. 按表 来组织 字段上下文
        # SQL 生成提示词通常按“表 -> 字段列表”的方式描述结构，
        # 所以这里先把分散的字段按 table_id 归到各自所属表下面。
        table_to_columns_map: dict[str, list[ColumnInfo]] = {}
        for column_info in retrieved_column_infos_map.values():
            table_id = column_info.table_id
            if table_id not in table_to_columns_map:
                table_to_columns_map[table_id] = []
            table_to_columns_map[table_id].append(column_info)

        # 5. 补齐主外键字段
        # 主外键通常不会出现在用户问题里，单靠向量召回容易漏掉；
        # 但多表查询的 Join 路径必须依赖它们，所以每张候选表都要兜底补齐。
        for table_id in table_to_columns_map.keys():
            # 通过表id获取该表所有字段
            key_columns: list[ColumnInfo] = await meta_mysql_repository.get_columns(table_id)
            column_ids = [column_info.id for column_info in table_to_columns_map[table_id]]
            for key_column in key_columns:
                if key_column.id not in column_ids:
                    table_to_columns_map[table_id].append(key_column)

        # 6. 生成表结构上下文
        # 数据库实体里可能包含入库和索引用字段，传给模型前只保留必要信息，
        # 让后续过滤和 SQL 生成节点面对的是更稳定的 TableInfoState 结构。 
        table_infos: list[TableInfoState] = []
        for table_id, column_infos in table_to_columns_map.items():
            table_info: TableInfo = await meta_mysql_repository.get_table(table_id)
            columns_state = [
                ColumnInfoState(
                    name=column_info.column_name,
                    type=column_info.type,
                    role=column_info.role,
                    description=column_info.description,
                    alias=column_info.alias,
                    examples=column_info.examples
                ) for column_info in column_infos
            ]
            table_info_state = TableInfoState(
                name=table_info.name,
                type=table_info.type,
                description=table_info.description,
                columns=columns_state
            )
            table_infos.append(table_info_state)

        # 7. 生成指标上下文
        # 指标上下文保留名称 描述 别名和依赖字段，足够让模型理解业务口径。
        metric_infos: list[MetricInfoState] = [
            MetricInfoState(
                name=retrieved_metric_info.name,
                description=retrieved_metric_info.description,
                relevant_columns=retrieved_metric_info.relevant_columns,
                alias=retrieved_metric_info.alias
            ) for retrieved_metric_info in retrieved_metric_infos
        ]

        logger.info(f"合并后的表信息：{[table_info['name'] for table_info in table_infos]}")
        logger.info(f"合并后的指标信息：{[metric_info['name'] for metric_info in metric_infos]}")

        writer({"type": "progress", "step": step, "status": "success"})
        return {
            "table_infos": table_infos,
            "metric_infos": metric_infos,
        }
    except Exception as e:
        logger.error(f"{step} failed: {e}")
        writer({"type": "progress", "step": step, "status": "error"})
        raise