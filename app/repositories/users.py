from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, delete
from pydantic import TypeAdapter
from typing import Any, List

from app import models
from app.schemas import users, posts
from app.redis import cache_or_db

user_response_list_adapter = TypeAdapter(List[users.UserResponse])
user_response_adapter = TypeAdapter(users.UserResponse)
user_response_security_adapter = TypeAdapter(users.UserResponseSecurity)
user_with_posts_adapter = TypeAdapter(posts.UserWithPosts)

class UserRepository:
    @staticmethod
    @cache_or_db("users:many", List[users.UserResponse])
    async def get_many(db: AsyncSession, limit: int = 5, offset: int = 0, search: str = "") -> List[users.UserResponse]:
        query = (
            select(models.User)
            .where(models.User.user_email.contains(search))
            .limit(limit)
            .offset(offset)
        )

        result = (await db.execute(query)).scalars().all()
        return user_response_list_adapter.validate_python(result)

    @staticmethod
    @cache_or_db("users:by_id", users.UserResponse)
    async def get_by_id(db: AsyncSession, user_id: int) -> users.UserResponse | None:
        query = (
            select(models.User)
            .where(models.User.user_id == user_id)
        )

        result = (await db.execute(query)).scalar_one_or_none()
        return user_response_adapter.validate_python(result) if result else None

    @staticmethod
    @cache_or_db("users:many", posts.UserWithPosts)
    async def get_user_by_id_with_posts(db: AsyncSession, user_id: int) -> posts.UserWithPosts | None:
        query = (
            select(models.User)
            .where(models.User.user_id == user_id)
            .options(selectinload(models.User.posts))
        )

        result = (await db.execute(query)).scalars().one_or_none()
        print(result)

        return user_with_posts_adapter.validate_python(result) if result else None
        
    @staticmethod
    # @cache_or_db("users:by_email", users.UserResponse)
    async def get_by_email(db: AsyncSession, user_email: str) -> users.UserResponse | None:
        query = (
            select(models.User)
            .where(models.User.user_email == user_email)
        )

        result = (await db.execute(query)).scalar_one_or_none()
        return user_response_adapter.validate_python(result) if result else None

    @staticmethod
    async def get_by_email_security(db: AsyncSession, user_email: str) -> users.UserResponseSecurity | None:
        query = (
            select(models.User)
            .where(models.User.user_email == user_email)
        )

        result = (await db.execute(query)).scalar_one_or_none()
        print(result)
        return user_response_security_adapter.validate_python(result) if result else None
    
    @staticmethod
    async def craete(db: AsyncSession, user_data: dict[str, Any]) -> users.UserResponse:
        new_user = models.User(**user_data)

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return user_response_adapter.validate_python(new_user)

    @staticmethod
    async def delete(db: AsyncSession, user_id: int) -> None:
        stmt = (
            delete(models.User)
            .where(models.User.user_id == user_id)
        )

        await db.execute(stmt)
        await db.commit()
        