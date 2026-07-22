from dataclasses import asdict
from app.entities.entity import ColumnMetric
from app.orm.column_metric_model import ColumnMetricMySQL

class ColumnMetricMapper:
    """ColumnMetric Entity <-> ORM"""

    @staticmethod
    def to_entity(orm: ColumnMetricMySQL) -> ColumnMetric:
        return ColumnMetric(
            column_id=orm.column_id,
            metric_id=orm.metric_id,
        )

    @staticmethod
    def to_ormmodel(entity: ColumnMetric) -> ColumnMetricMySQL:
        return ColumnMetricMySQL(**asdict(entity))