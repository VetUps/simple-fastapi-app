from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app import models
from typing import Any

class UserRepository:
    @staticmethod
    async def get_many(db: AsyncSession, limit: int = 5, offset: int = 0, search: str = ""):
        query = (
            select(models.User)
            .where(models.User.user_email.contains(search))
            .limit(limit)
            .offset(offset)
        )

        result = (await db.execute(query)).scalars().all()
        return result

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int):
        query = (
            select(models.User)
            .where(models.User.user_id == user_id)
        )

        result = (await db.execute(query)).scalar_one_or_none()
        return result

    @staticmethod
    async def get_by_email(db: AsyncSession, user_email: str):
        query = (
            select(models.User)
            .where(models.User.user_email == user_email)
        )

        result = (await db.execute(query)).scalar_one_or_none()
        return result

    @staticmethod
    async def craete(db: AsyncSession, user_data: dict[str, Any]):
        new_user = models.User(**user_data)

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user