from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, delete

from app import models
from typing import Any, Sequence

class UserRepository:
    @staticmethod
    async def get_many(db: AsyncSession, limit: int = 5, offset: int = 0, search: str = "") -> Sequence[models.User]:
        query = (
            select(models.User)
            .where(models.User.user_email.contains(search))
            .limit(limit)
            .offset(offset)
        )

        result = (await db.execute(query)).scalars().all()
        return result

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> models.User | None:
        query = (
            select(models.User)
            .where(models.User.user_id == user_id)
        )

        result = (await db.execute(query)).scalar_one_or_none()
        return result

    @staticmethod
    async def get_user_by_id_with_posts(db: AsyncSession, user_id: int) -> models.User | None:
        query = (
            select(models.User)
            .where(models.User.user_id == user_id)
            .options(selectinload(models.User.posts))
        )

        result = (await db.execute(query)).scalars().one_or_none()
        return result
        
    @staticmethod
    async def get_by_email(db: AsyncSession, user_email: str) -> models.User | None:
        query = (
            select(models.User)
            .where(models.User.user_email == user_email)
        )

        result = (await db.execute(query)).scalar_one_or_none()
        return result

    @staticmethod
    async def craete(db: AsyncSession, user_data: dict[str, Any]) -> models.User:
        new_user = models.User(**user_data)

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user

    @staticmethod
    async def delete(db: AsyncSession, user_id: int) -> None:
        stmt = (
            delete(models.User)
            .where(models.User.user_id == user_id)
        )

        await db.execute(stmt)
        await db.commit()
        