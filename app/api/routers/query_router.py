from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.schema.query_schema import QuerySchema
from app.services.query_service import QueryService
from app.api.dependencies import get_query_service

query_router = APIRouter(
    prefix="/E-commerce",
    tags=["Agent"]
)

@query_router.post("/query")
async def query_handle(
    # query: QuerySchema
    # FastAPI 会检查这个参数的类型。
    # 如果它发现这是一个 Pydantic 模型（BaseModel 的子类），
    # 它会自动判定：这个参数的数据应该从 HTTP 请求体（Request Body）中读取。
    query: QuerySchema, 
    query_service: Annotated[QueryService, Depends(get_query_service)]
    ):

    """接收用户自然语言问题，并流式返回 LangGraph 工作流输出"""

    return StreamingResponse(
        # query.query 是用户问题字符串；QueryService.query 返回异步生成器供响应逐段消费
        query_service.query(query.query, query.user_id, query.session_id),
        media_type="text/event-stream",
    )