from pathlib import Path
from omegaconf import OmegaConf
from dataclasses import dataclass
from typing import Optional

@dataclass
class ColumnConfig:
    """
    单个字段的同步配置
    描述字段的业务角色 说明 别名以及是否同步字段值
    """
    name: str
    role: str
    description: str
    alias: list[str]
    sync: bool


@dataclass
class TableConfig:
    """
    单张表及其字段列表的同步配置
    一张表下面会继续声明需要纳入知识库的字段列表
    """
    name: str
    role: str
    description: str
    columns: list[ColumnConfig]


@dataclass
class MetricConfig:
    """
    单个指标的同步配置
    用来描述指标和底层字段之间的关联关系
    """
    name: str
    description: str
    relevant_columns: list[str]
    alias: list[str]


@dataclass
class MetaConfig:
    """
    元数据知识构建总配置
    tables 和 metrics 都允许为空 便于分阶段只构建其中一部分
    """
    tables: Optional[list[TableConfig]] = None
    metrics: Optional[list[MetricConfig]] = None

meta_config_file = Path(__file__).parents[2] / "config" / "meta_config.yaml"
meta_context = OmegaConf.load(meta_config_file)

# print(meta_context, type(meta_context))
schema = OmegaConf.structured(MetaConfig)
metaconfig: MetaConfig = OmegaConf.to_object(OmegaConf.merge(schema, meta_context))

if __name__ == "__main__":
    print(metaconfig.tables[0])
    print(type(metaconfig))


