import uuid
from pathlib import Path
from fastapi import UploadFile

PROJECT_ROOT = Path(__file__).resolve().parents[2]
print(PROJECT_ROOT) # D:\VScodeProjects\Agent_Learning\个人项目实战\E-commerce

AVATAR_DIR = PROJECT_ROOT / "static" / "avatar"

async def save_avatar(file: UploadFile):
    # 创建目录
    AVATAR_DIR.mkdir(parents=True,exist_ok=True)

    # 获取文件后缀
    suffix = Path(file.filename).suffix

    # 生成唯一文件名
    filename = (f"{uuid.uuid4()}{suffix}")
    filepath = (AVATAR_DIR / filename)

    # 写入文件
    content = await file.read()
    with open(filepath,"wb") as f:
        f.write(content)

    # 返回访问路径
    return f"/static/avatar/{filename}"