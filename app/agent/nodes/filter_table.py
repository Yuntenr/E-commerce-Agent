import yaml
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.state import DataAgentState, TableInfoState
from app.agent.context import DataAgentContext
from app.common.logger import logger
from app.prompts.loader_prompt import load_prompt
from app.agent.llm import llm_model

"""根据用户问题裁剪候选表结构上下文"""
async def filter_table(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    step = "过滤表信息"
    writer({"type": "progress", "step": step, "status": "running"})

    try:
        query = state["rewritten_query"]
        table_infos: list[TableInfoState] = state["table_infos"]

        prompt = PromptTemplate(
            template=load_prompt("filter_table_info"),
            input_variables=["query", "table_infos"]
        )
        json_parser = JsonOutputParser()
        chain = prompt | llm_model | json_parser

        # table_infos 是嵌套结构，转成 YAML 后更适合放进提示词，也保留中文字段说明
        table_infos_to_yaml = yaml.dump(data=table_infos, allow_unicode=True, sort_keys=False)
        """
        输出格式（严格遵守）：
        {{
        "表名1":["字段1", "字段2", "..."],
        "表名2":["字段1", "字段2", "..."]
        }}
        """
        result = await chain.ainvoke(input={"query": query, "table_infos": table_infos_to_yaml})

        # 模型只负责选择，程序根据选择结果从原始 TableInfoState 中裁剪，避免模型重写复杂结构出错
        filtered_table_infos: list[TableInfoState] = []
        for table_info in table_infos:
            if table_info["name"] in result:
                table_info["columns"] = [
                    column_info for column_info in table_info["columns"] if column_info["name"] in result[table_info["name"]]
                ]
                filtered_table_infos.append(table_info)

        logger.info(f"过滤后的表信息：{[filtered_table_info['name'] for filtered_table_info in filtered_table_infos]}")
        writer({"type": "progress", "step": step, "status": "success"})
        return {"table_infos": filtered_table_infos}
    
    except Exception as e:
        logger.error(f"{step} failed: {e}")
        writer({"type": "progress", "step": step, "status": "error"})
        raise

