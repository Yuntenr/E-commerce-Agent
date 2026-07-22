from typing import Annotated
from fastapi import APIRouter, Depends, Form, UploadFile, File

from app.services.frontend_service import RegisterService
from app.api.dependencies import get_register_service
from app.common.save_avatar import save_avatar


register_router = APIRouter(
    prefix="/E-commerce",
    tags=["Agent"]
)

@register_router.post("/register")
async def register(
    username: str = Form(...),
    password: str = Form(...),
    avatar: UploadFile | None = File(None),
    register_service: Annotated[RegisterService, Depends(get_register_service)] = None
):
    print("收到注册请求")
    print(username, password)

    avatar_path = None
    if avatar:
        avatar_path = await save_avatar(avatar)

    user = await register_service.register(
        username=username,
        password=password,
        avatar=avatar_path
    )

    return {
        "id": user.id,
        "username": user.username,
        "avatar": user.avatar
    }
