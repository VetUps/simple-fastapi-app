from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql.expression import text
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey

class Base(DeclarativeBase):
    pass

class Post(Base):
    __tablename__ = "posts"

    post_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    post_title = Column(String, nullable=False)
    post_content = Column(String, nullable=False)
    post_published = Column(Boolean, nullable=False, server_default=text('True'))
    post_created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    user = relationship("User")

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_email = Column(String, nullable=False, unique=True)
    user_password = Column(String, nullable=False)
    user_created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
