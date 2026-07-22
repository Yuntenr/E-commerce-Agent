"""
FastAPI 应用入口

负责创建后端应用实例，注册应用生命周期函数，并把各业务模块中的 router
挂载到同一个 app 上。HTTP 请求会先进入这里创建的 app，再按路由分发到
具体的接口处理函数。
"""

import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.lifespan import lifespan
from app.api.routers.query_router import query_router
from app.api.routers.register_router import register_router
from app.api.routers.login_router import login_router
from app.common.context import request_id_ctx_var

# lifespan 交给 FastAPI 管理，用于在服务启动和关闭时统一初始化与释放外部客户端
app = FastAPI(lifespan=lifespan)

# 添加 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=[
        "*"
    ],
    allow_headers=[
        "*"
    ],
)

# 把查询路由注册进应用；没有挂载时，/docs 和真实 HTTP 请求都访问不到该接口
app.include_router(login_router)
app.include_router(register_router)
app.include_router(query_router)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    # 请求被处理之前
    request_id = uuid.uuid4()
    request_id_ctx_var.set(request_id)

    #call_next 是 FastAPI 中间件（middleware）里的一个回调函数，把当前请求继续传递给后续的处理流程，然后拿到最终响应。
    response = await call_next(request)
    # 请求被处理之后
    return response
