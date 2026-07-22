from langchain_openai.chat_models import ChatOpenAI
from app.config.app_config import appconfig

llm_model = ChatOpenAI(
    model=appconfig.llm.model_name,
    api_key=appconfig.llm.api_key,
    base_url=appconfig.llm.base_url,
    # 字段扩展、SQL 生成更看重稳定性，所以这里关闭随机发散
    temperature=0,
)

if __name__ == "__main__":
    res = llm_model.invoke(input="你是谁？")  # 记得关梯子
    print(res.content)
