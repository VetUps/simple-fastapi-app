from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app import models

class VoteRepository:
    @staticmethod
    async def get_by_user_post_id(db: AsyncSession, post_id: int, user_id: int):
        stmt = (
            select(models.Vote)
            .where(models.Vote.post_id == post_id, models.Vote.user_id == user_id)
        )
        result = (await db.execute(stmt)).scalar_one_or_none()

        return result

    @staticmethod
    async def create(db: AsyncSession, post_id: int, user_id: int):
        stmt = (
            insert(models.Vote)
            .values(post_id=post_id, user_id=user_id)
            .returning(models.Vote)
        )

        result = (await db.execute(stmt)).scalar_one_or_none()
        await db.commit()

        return result

    @staticmethod
    async def delete(db: AsyncSession, post_id: int, user_id: int):
        stmt = (
            delete(models.Vote)
            .where(models.Vote.post_id == post_id, models.Vote.user_id == user_id)
        )

        await db.execute(stmt)
        await db.commit()
