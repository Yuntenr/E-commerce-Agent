import json
import yaml

from langgraph.runtime import Runtime
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from app.agent.state import DataAgentState, ContextEntity
from app.agent.context import DataAgentContext
from app.common.logger import logger
from app.agent.llm import llm_model
from app.prompts.loader_prompt import load_prompt

async def extract_entities(state: DataAgentState, runtime:Runtime[DataAgentContext]):
    step = "抽取可能被引用的实体"
    writer = runtime.stream_writer
    writer({"type": "progress","step": step, "status": "running"})

    try:
        query = state["query"]
        sql_result = state["sql_result"]

        prompt = PromptTemplate(
            template=load_prompt("extract_entities"),
            input_variables=["query", "sql_result"]
        )

        str_parser = StrOutputParser()
        chain = prompt | llm_model | str_parser

        sql_result_to_yaml = yaml.dump(data=sql_result, allow_unicode=True, sort_keys=False)
        result = await chain.ainvoke(input={"query": query, "sql_result": sql_result_to_yaml})
        # 将抽取的实体result放入state中
        # 解析LLM JSON结果
        entities_json = json.loads(result)
        entities: list[ContextEntity] = []
        for item in entities_json:
            entity: ContextEntity = {
                "type": item["type"],
                "name": item["name"],
                "source": "sql_result"
            }
            entities.append(entity)

        writer({"type": "progress","step": step,"status": "success"})
        logger.info(f"抽取实体成功:{result}")
        return  {"new_entities": entities}
    
    except Exception as e:
        logger.error(f"抽取实体失败:{e}")
        writer({"type": "progress","step": step,"status": "error"})
        raise