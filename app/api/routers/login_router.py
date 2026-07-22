from typing import Annotated
from fastapi import APIRouter, Depends, Form
from app.services.frontend_service import LoginService
from app.api.dependencies import get_login_service
from app.entities.entity import UserInfo
from app.api.schema.login_schema import LoginRequest

login_router = APIRouter(
    prefix="/E-commerce",
    tags=["Agent"]
)

@login_router.post("/login")
async def login(
    login_data: LoginRequest,
    login_service: Annotated[LoginService, Depends(get_login_service)] = None
):
    username = login_data.username
    password = login_data.password
    result: UserInfo = await login_service.login(username, password)

    return {
        "id": result.id,
        "username": result.username,
        "avatar": result.avatar
    }

    
