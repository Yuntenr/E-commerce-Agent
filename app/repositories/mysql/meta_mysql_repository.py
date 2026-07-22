from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.entities.entity import TableInfo, ColumnInfo, ColumnMetric, MetricInfo
from app.mapper.table_info_mapper import TableInfoMapper
from app.mapper.column_info_mapper import ColumnInfoMapper
from app.mapper.metric_info_mapper import MetricInfoMapper
from app.mapper.column_metric_mapper import ColumnMetricMapper
from app.orm.table_info_model import TableInfoMySQL
from app.orm.column_info_model import ColumnInfoMySQL
from app.orm.column_metric_model import ColumnMetricMySQL
from app.orm.metric_info_model import MetricInfoMySQL

class MetaMySQLRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ==========================
    # Table
    # ==========================
    async def save_table(self, table_info: TableInfo):
        orm = TableInfoMapper.to_ormmodel(table_info)
        self.session.add(orm)

    async def get_table(self, table_id: str) -> TableInfo | None:
        orm = await self.session.get(TableInfoMySQL, table_id)

        if orm is None:
            return None

        return TableInfoMapper.to_entity(orm)

    async def list_tables(self) -> list[TableInfo]:
        stmt = select(TableInfoMySQL)

        result = await self.session.execute(stmt)

        return [
            TableInfoMapper.to_entity(item)
            for item in result.scalars().all()
        ]

    async def delete_table(self, table_id: str):
        orm = await self.session.get(TableInfoMySQL, table_id)

        if orm is not None:
            await self.session.delete(orm)

    # ==========================
    # Column
    # ==========================
    async def save_column(self, column_info: ColumnInfo):
        orm = ColumnInfoMapper.to_ormmodel(column_info)
        self.session.add(orm)

    async def get_column(self, column_id: str) -> ColumnInfo | None:
        orm = await self.session.get(ColumnInfoMySQL, column_id)

        if orm is None:
            return None

        return ColumnInfoMapper.to_entity(orm)

    async def get_columns(self, table_id: str) -> list[ColumnInfo]:
        stmt = (
            select(ColumnInfoMySQL)
            .where(ColumnInfoMySQL.table_id == table_id)
        )

        result = await self.session.execute(stmt)

        return [
            ColumnInfoMapper.to_entity(item)
            for item in result.scalars().all()
        ]

    # ==========================
    # Metric
    # ==========================
    async def save_metric(self, metric_info: MetricInfo):
        orm = MetricInfoMapper.to_ormmodel(metric_info)
        self.session.add(orm)

    async def get_metric(self, metric_id: str) -> MetricInfo | None:
        orm = await self.session.get(MetricInfoMySQL, metric_id)

        if orm is None:
            return None

        return MetricInfoMapper.to_entity(orm)

    async def list_metrics(self) -> list[MetricInfo]:
        stmt = select(MetricInfoMySQL)

        result = await self.session.execute(stmt)

        return [
            MetricInfoMapper.to_entity(item)
            for item in result.scalars().all()
        ]
    
    # ==========================
    # ColumnMetric
    # ==========================
    async def save_column_metric(self, column_metric: ColumnMetric):
        orm = ColumnMetricMapper.to_ormmodel(column_metric)
        self.session.add(orm)

    async def get_column_metrics(self, metric_id: str) -> list[ColumnMetric]:
        stmt = (
           select(ColumnMetricMySQL)
           .where(ColumnMetricMySQL.metric_id == metric_id)
        )
        result = await self.session.execute(stmt)

        return [
            ColumnMetricMapper.to_entity(item)
            for item in result.scalars().all()
        ]

    async def get_metric_columns(self, column_id: str) -> list[ColumnMetric]:
        stmt = (
            select(ColumnMetricMySQL)
            .where(ColumnMetricMySQL.column_id == column_id)
        )

        result = await self.session.execute(stmt)

        return [
            ColumnMetricMapper.to_entity(item)
            for item in result.scalars().all()
        ]
    

    # ==========================
    # Transaction
    # ==========================
    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()