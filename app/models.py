from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy.sql.expression import text
from sqlalchemy import ForeignKey

from typing import Annotated
from datetime import datetime

intpk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime, mapped_column(server_default=text("now()"))]
updated_at = Annotated[datetime, mapped_column(server_default=text("now()"), server_onupdate=text("now()"))]

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[intpk]
    user_email: Mapped[str] = mapped_column(unique=True)
    user_password: Mapped[str]
    user_created_at: Mapped[created_at]
    user_updated_at: Mapped[updated_at]

class Post(Base):
    __tablename__ = "posts"

    post_id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))
    post_title: Mapped[str]
    post_content: Mapped[str]
    post_published: Mapped[bool] = mapped_column(server_default="True")
    post_created_at: Mapped[created_at]

    user: Mapped[User] = relationship("User")

class Vote(Base):
    __tablename__ = "votes"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.post_id", ondelete="CASCADE"), primary_key=True)
