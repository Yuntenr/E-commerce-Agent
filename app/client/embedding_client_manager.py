import asyncio
import inspect
from typing import Optional
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from huggingface_hub import AsyncInferenceClient
from app.config.app_config import appconfig, EmbeddingConfig

""" 
1、langchain_huggingface >= 1.2.2后，不在支持model=url，但其底层huggingface_hub依然支持
2、记得关梯子，不然一直502 Bad Gateway，被恶心了一下午
"""

class EmbeddingClientManager:
    """管理本地 Embedding 模型"""
    def __init__(self, config: EmbeddingConfig):
        self.client: Optional[AsyncInferenceClient] = None
        self.config = config

    def _get_url(self) -> str:
        """拼接 Embedding 服务地址"""
        return f"http://{self.config.host}:{self.config.port}"
    
    def init(self):
        """显式初始化客户端，避免模块导入时立即建立外部连接"""
        self.client = AsyncInferenceClient(model=self._get_url())  # 链接text embedding model

# 模块级单例，供整个项目复用同一套 Embedding 客户端管理器
embedding_client_manager = EmbeddingClientManager(appconfig.embedding)

if __name__ == "__main__":
    embedding_client_manager.init()
    client = embedding_client_manager.client

    async def test():
        """执行一次最小化向量化调用，验证服务是否可用"""
        text = "What is deep learning?"
        query_result = await client.feature_extraction(text)
        print(query_result[0])

    asyncio.run(test())
    