from dataclasses import asdict
from app.entities.entity import MetricInfo
from app.orm.metric_info_model import MetricInfoMySQL

class MetricInfoMapper:
    """MetricInfo Entity <-> ORM"""

    @staticmethod
    def to_entity(orm: MetricInfoMySQL) -> MetricInfo:
        return MetricInfo(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            relevant_columns=orm.relevant_columns,
            alias=orm.alias,
        )

    @staticmethod
    def to_ormmodel(entity: MetricInfo) -> MetricInfoMySQL:
        return MetricInfoMySQL(**asdict(entity))