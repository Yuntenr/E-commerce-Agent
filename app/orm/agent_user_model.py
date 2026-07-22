from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, BigInteger

from app.orm.base import Base

class UserInfoMySQL(Base):
    __tablename__ = "agent_user"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    password: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    avatar: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )