from pydantic import BaseModel
from app.entities.entity import UserInfo

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo