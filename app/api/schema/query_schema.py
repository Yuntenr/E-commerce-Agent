from pydantic import BaseModel

class QuerySchema(BaseModel):
    query: str                    # 必填，字符串
    user_id: int
    session_id: str | None = None
