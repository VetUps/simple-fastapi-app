from sqlalchemy import select, insert, delete, exists
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import TypeAdapter

from app import models
from app.schemas import votes
from app.redis import cache_or_db, invalidate_cache

vote_adapter = TypeAdapter(votes.Vote)

class VoteRepository:
    @staticmethod
    @cache_or_db("votes:one", votes.Vote)
    async def get_by_user_post_id(db: AsyncSession, post_id: int, user_id: int) -> votes.Vote:
        query = (
            select(models.Vote)
            .where(models.Vote.post_id == post_id, models.Vote.user_id == user_id)
        )
        result = (await db.execute(query)).scalar_one()
        
        return vote_adapter.validate_python(result)

    @staticmethod
    @invalidate_cache("votes")
    async def create(db: AsyncSession, post_id: int, user_id: int) -> votes.Vote:
        stmt = (
            insert(models.Vote)
            .values(post_id=post_id, user_id=user_id)
            .returning(models.Vote)
        )

        result = (await db.execute(stmt)).scalar_one_or_none()
        await db.commit()

        return vote_adapter.validate_python(result)

    @staticmethod
    @invalidate_cache("votes")
    async def delete(db: AsyncSession, post_id: int, user_id: int) -> None:
        stmt = (
            delete(models.Vote)
            .where(models.Vote.post_id == post_id, models.Vote.user_id == user_id)
        )

        await db.execute(stmt)
        await db.commit()

    @staticmethod
    async def is_exists(db: AsyncSession, post_id: int, user_id: int) -> bool:
        """
        Проверяет факт существования голоса по post_id и user_id
        """
        query = select(
            exists(
                select(models.Vote)
                .where(models.Vote.post_id == post_id, models.Vote.user_id == user_id)
            )
        )

        result = (await db.execute(query)).scalar_one()

        return result
    