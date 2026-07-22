import yaml
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.runtime import Runtime

from app.agent.llm import llm_model
from app.agent.state import DataAgentState, HistoryQA, ContextEntity
from app.agent.context import DataAgentContext
from app.common.logger import logger
from app.prompts.loader_prompt import load_prompt
from app.common.is_need_rewrite import need_query_rewrite


async def  resolve_context_node(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    step = "问题改写"
    writer = runtime.stream_writer
    writer({"type": "progress", "step": step, "status": "running"})

    try:
        query = state["query"]
        # 使用get，如果第一轮没有初始化，会报错
        history = state.get("history", [])
        entities = state.get("active_entities", [])

        if not need_query_rewrite(query, history, entities):
            writer({"type": "progress", "step": step, "status": "success"})
            logger.info(f"问题无需改写: {query}")
            return {"rewritten_query": query}

        prompt = PromptTemplate( 
            template=load_prompt("query_rewrite"),
            input_variables=["history", "active_entities", "query"]
        )
        str_parser = StrOutputParser()
        chain = prompt | llm_model | str_parser

        history_to_yaml = yaml.dump(data=history, allow_unicode=True, sort_keys=False)
        entities_to_yaml = yaml.dump(data=entities, allow_unicode=True, sort_keys=False)
        result = await chain.ainvoke(input={"history": history_to_yaml, "active_entities": entities_to_yaml, "query": query})

        rewritten_query = result.strip()

        writer({"type": "progress", "step": step, "status": "success"})
        logger.info(f"问题改写成功: {rewritten_query}")
        return {"rewritten_query": rewritten_query}
    
    except Exception as e:
        logger.error(f"问题改写失败: {e}")
        writer({"type": "progress", "step": step, "status": "error"})
        raise

        