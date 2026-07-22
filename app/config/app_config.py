from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv
from omegaconf import OmegaConf

@dataclass
class File:
    """文件日志配置"""
    enable: bool
    level: str
    path: str
    rotation: str
    retention: str


@dataclass
class Console:
    """控制台日志配置"""
    enable: bool
    level: str

@dataclass
class LoggingConfig:
    """日志总配置"""
    file: File
    console: Console

@dataclass
class DBConfig:
    """MySQL 连接配置"""
    host: str
    port: int
    user: str
    password: str
    database: str

@dataclass
class QdrantConfig:
    """Qdrant 连接与向量维度配置"""
    host: str
    port: int
    embedding_size: int

@dataclass
class EmbeddingConfig:
    """Embedding 服务配置"""
    host: str
    port: int
    model: str

@dataclass
class ESConfig:
    """Elasticsearch 配置"""
    host: str
    port: int
    index_name: str

@dataclass
class RedisConfig:
    host: str
    port: int
    db: int
    password: str | None
    expire: int
    prefix: str

@dataclass
class LLMConfig:
    """大模型调用配置"""
    model_name: str
    api_key: str
    base_url: str


@dataclass
class AppConfig:
    """项目级总配置入口"""
    logging: LoggingConfig
    meta_db: DBConfig
    dw_db: DBConfig
    user_db: DBConfig
    qdrant: QdrantConfig
    embedding: EmbeddingConfig
    es: ESConfig
    redis: RedisConfig
    llm: LLMConfig

# 先从当前位置回到项目根目录，再用[3]定位到config/app_config.yaml的上一级目录
project_root = Path(__file__).parents[2]
# print("=====", project_root)

# 从.env 提取部分敏感config
load_dotenv(project_root / ".env")

config_file = project_root / "config" / "app_config.yaml"
# print(config_file)

context = OmegaConf.load(config_file)
# print(context)
# print(type(context))

schema = OmegaConf.structured(AppConfig)
appconfig: AppConfig = OmegaConf.to_object(OmegaConf.merge(schema, context))

if __name__ == "__main__":
    print(appconfig.logging.file.path)
