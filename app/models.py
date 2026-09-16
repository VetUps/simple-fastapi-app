from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy.sql.expression import text
from sqlalchemy import ForeignKey, Enum

from typing import Annotated, List
from datetime import datetime
import enum

intpk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime, mapped_column(server_default=text("now()"))]
updated_at = Annotated[datetime, mapped_column(server_default=text("now()"), onupdate=datetime.now())]

class Base(DeclarativeBase):
    pass

class UserRole(enum.Enum):
    ADIM = "admin"
    USER = "user"
    GUEST = "guest"

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[intpk]
    user_email: Mapped[str] = mapped_column(unique=True)
    user_password: Mapped[str]
    user_role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role_enum"), nullable=False, default=UserRole.USER)
    user_created_at: Mapped[created_at]
    user_updated_at: Mapped[updated_at]

    posts: Mapped[List[Post]] = relationship("Post", back_populates="user", cascade="all, delete-orphan")

class Vote(Base):
    __tablename__ = "votes"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.post_id", ondelete="CASCADE"), primary_key=True)
    
class Post(Base):
    __tablename__ = "posts"

    post_id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))
    post_title: Mapped[str]
    post_content: Mapped[str]
    post_published: Mapped[bool] = mapped_column(server_default=text("true"))
    post_created_at: Mapped[created_at]

    user: Mapped[User] = relationship("User", back_populates="posts")
    votes: Mapped[List[Vote]] = relationship("Vote")
