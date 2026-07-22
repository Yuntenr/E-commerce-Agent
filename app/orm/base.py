from sqlalchemy.orm import DeclarativeBase
"""
这里的 Base 是 所有 ORM 模型的父类，它告诉 SQLAlchemy：
"继承我的类，都是数据库表。"
"""
class Base(DeclarativeBase):
    pass