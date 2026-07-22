import uuid
import numpy as np
from dataclasses import asdict
from pathlib import Path
from huggingface_hub import AsyncInferenceClient
from app.config.meta_config import metaconfig, MetaConfig
from app.entities.entity import TableInfo, ColumnInfo, MetricInfo, ColumnMetric, ValueInfo
from app.repositories.mysql.meta_mysql_repository import MetaMySQLRepository
from app.repositories.mysql.dw_repository import DwRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.es.value_es_repository import ValueESRepository
from app.common.logger import logger
from app.common.convert_to_qdrant_format import convert_batch_to_qdrant

class MetaDBService:
    def __init__(self,
                 meta_mysql_repository: MetaMySQLRepository,
                 dw_repository: DwRepository,
                 metric_qdrant_repository: MetricQdrantRepository,
                 column_qdrant_repository: ColumnQdrantRepository,
                 value_es_repository: ValueESRepository,
                 embedding_client: AsyncInferenceClient):
        
        self.meta_mysql_repository=meta_mysql_repository
        self.dw_repository=dw_repository
        self.metric_qdrant_repository=metric_qdrant_repository
        self.column_qdrant_repository=column_qdrant_repository
        self.value_es_repository=value_es_repository
        self.embedding_client = embedding_client

    "导入表和字段信息到meta_db"
    async def _save_tables_meta_db(self, metaconfig: MetaConfig):
        table_infos: list[TableInfo] = []
        column_infos: list[ColumnInfo] = []

        # tables: list[TableConfig] --> TableInfo entity
        for table in metaconfig.tables:
            table_info = TableInfo(
                id=table.name,
                name=table.name,
                type=table.role,  # 表类型 fact/dim
                description=table.description
            )
            # input: TableInfo(entity)-->调用save_table-->ORM-->存入meta_db
            await self.meta_mysql_repository.save_table(table_info)  # to save table_info
            
            # 从dw数据库中查找字段的类型
            column_types = await self.dw_repository._get_column_type(table_name=table.name)
            # table.columns: list[ColumnConfig]
            for column in table.columns:
                # 拿少量示例值(example)，目的是让字段元数据更容易被人和模型理解
                column_values = await self.dw_repository.get_column_values(table.name, column.name)
                column_info = ColumnInfo(
                    id=f"{table.name}.{column.name}",
                    table_id=table.name,
                    column_name=column.name,
                    type=column_types[column.name],
                    description=column.description,
                    alias=column.alias,
                    role=column.role,
                    examples=column_values
                )
                column_infos.append(column_info)
                await self.meta_mysql_repository.save_column(column_info)  # to save column_info
        # 所有表和字段保存完后，一次性提交
        await self.meta_mysql_repository.commit()
        return column_infos
    
    "导入metric指标信息到meta_db"
    async def _save_metrics_to_meta_db(self, metaconfig: MetaConfig):
        
        metric_infos: list[MetricInfo] = []
        # metrics: list[MetaConfig]-->MetricInfo
        for metric in metaconfig.metrics:
            metric_info = MetricInfo(
                id=metric.name,
                name=metric.name,
                description=metric.description,
                relevant_columns=metric.relevant_columns,
                alias=metric.alias
            )
            metric_infos.append(metric_info)
            # input: MetricInfo(entity)-->调用save_table-->ORM-->存入meta_db
            await self.meta_mysql_repository.save_metric(metric_info)  # to save metric_info

            for column in metric.relevant_columns:
                column_metric = ColumnMetric(
                    column_id=column,
                    metric_id=metric.name
                )
                await self.meta_mysql_repository.save_column_metric(column_metric)  # to save column_metric
        # 所有表和字段保存完后，一次性提交
        await self.meta_mysql_repository.commit()
        return metric_infos
    
    """将字段真实取值存入es中"""
    async def _save_value_info_to_es(self, column_infos: list[ColumnInfo]):
        await self.value_es_repository.ensure_index()

        # 不是所有字段都要同步真实值，是否同步由配置里的 sync 显式控制
        column2sync: dict[str, bool] = {}
        for table in metaconfig.tables:
            for column in table.columns:
                column2sync[f"{table.name}.{column.name}"] = column.sync

        value_infos: list[ValueInfo] = []
        for column_info in column_infos:
            sync = column2sync[column_info.id]
            if sync:
                # 这里拿的是字段真实值全集，不再是少量 examples
                current_column_values = (
                    await self.dw_repository.get_column_values(
                        column_info.table_id, column_info.column_name, 100000
                    )
                )
                current_values_infos = [
                    ValueInfo(
                        id=f"{column_info.id}.{current_column_value}",
                        value=current_column_value,
                        column_id=column_info.id,
                    )
                    for current_column_value in current_column_values
                ]
                value_infos.extend(current_values_infos)

        await self.value_es_repository.index(value_infos)


    """存入qdrant向量库"""
    async def _save_columns_to_qdrant(self, column_infos: list[ColumnInfo]):
        await self.column_qdrant_repository.ensure_collection()
        points: list[dict] = []
        for column_info in column_infos:
            points.append(
                {
                    "id": uuid.uuid4(),
                    "embedding_text": column_info.column_name,
                    "payload": asdict(column_info)
                }
            )

            points.append(
                {
                    "id": uuid.uuid4(),
                    "embedding_text": column_info.description,
                    "payload": asdict(column_info)
                }
            )

            for alia in column_info.alias:
                points.append(
                    {
                        "id": uuid.uuid4(),
                        "embedding_text": alia,
                        "payload": asdict(column_info)
                    }
                )  
        ids: list[str] = [point["id"] for point in points]
        payloads: list[dict] =  [point["payload"] for point in points]
        # 调用Embedding模型将embedding_text-->vector
        vectors: list[list[float]] = []
        embedding_texts: list[str] = [point["embedding_text"] for point in points]
        embedding_batch_size = 10
        for i in range(0, len(embedding_texts), embedding_batch_size):
            batch_embedding_texts = embedding_texts[i : i + embedding_batch_size]
            batch_vectors_np = await self.embedding_client.feature_extraction(batch_embedding_texts)
            batch_vectors = convert_batch_to_qdrant(batch_vectors_np)
            vectors.extend(batch_vectors)
        # 存入向量库
        await self.column_qdrant_repository.upsert(ids, vectors, payloads)          

    async def _save_metrics_to_qdrant(self, metric_infos: list[MetricInfo]):
        await self.metric_qdrant_repository.ensure_collection()

        points: list[dict] = []
        for metric_info in metric_infos:
            points.append(
                {
                    "id": uuid.uuid4(),
                    "embedding_text": metric_info.name,
                    "payload": asdict(metric_info)
                }
            )

            points.append(
                {
                    "id": uuid.uuid4(),
                    "embedding_text": metric_info.description,
                    "payload": asdict(metric_info)
                }
            )

            for alia in metric_info.alias:
                points.append(
                    {
                        "id": uuid.uuid4(),
                        "embedding_text": alia,
                        "payload": asdict(metric_info)
                    }
                )
        ids: list[str] = [point["id"] for point in points]
        payloads: list[dict] =  [point["payload"] for point in points]
        # 调用Embedding模型将embedding_text-->vector
        vectors: list[list[float]] = []
        embedding_texts: list[str] = [point["embedding_text"] for point in points]
        embedding_batch_size = 10
        for i in range(0, len(embedding_texts), embedding_batch_size):
            batch_embedding_texts = embedding_texts[i : i + embedding_batch_size]
            batch_vectors_np = await self.embedding_client.feature_extraction(batch_embedding_texts)
            batch_vectors = convert_batch_to_qdrant(batch_vectors_np)
            vectors.extend(batch_vectors)
        # 存入向量库
        await self.metric_qdrant_repository.upsert(ids, vectors, payloads)

        
    async def build(self):
        if metaconfig.tables:   
            # 将表信息和字段信息保存到 Meta MySQL
            column_infos: list[ColumnInfo] = await self._save_tables_meta_db(metaconfig)    
            logger.info("保存表信息和字段信息到 Meta MySQL")

            # 对字段信息建立向量索引
            await self._save_columns_to_qdrant(column_infos)
            logger.info("为字段信息建立向量索引")

            # 对指定的维度字段取值建立全文索引
            await self._save_value_info_to_es(column_infos)
            logger.info("为字段取值建立全文索引")
        
        if metaconfig.metrics:
            # 将指标信息和字段依赖关系保存到 Meta MySQL
            metric_infos: list[MetricInfo] = await self._save_metrics_to_meta_db(metaconfig)
            logger.info("保存指标信息到数据库成功")

            # 对指标信息建立向量索引
            await self._save_metrics_to_qdrant(metric_infos)
            logger.info("为指标信息建立向量索引成功")


