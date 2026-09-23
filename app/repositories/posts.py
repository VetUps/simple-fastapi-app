from sqlalchemy import Row, select, delete, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload
from typing import Any, List, Sequence, Tuple

from app import models
from app.redis import cache_or_db
from app.schemas import posts

class PostRepository:
    @staticmethod
    @cache_or_db("posts:many", List[posts.PostResponseWithVotes])
    async def get_many(db: AsyncSession, limit: int = 5, offset: int = 0, search: str = "") -> Sequence[Row[Tuple[models.Post, int]]]:
        """
        Возвращает пагинированные посты
        """ 

        query = (
            select(models.Post, func.count(models.Vote.user_id).label("votes"))
            .join(models.Post.user)
            .options(contains_eager(models.Post.user))
            .outerjoin(models.Vote, models.Post.post_id  == models.Vote.post_id)
            .where(models.Post.post_title.contains(search))
            .group_by(models.Post.post_id, models.User.user_id)
            .limit(limit)
            .offset(offset)
        )

        # print(query.compile(compile_kwargs={"literal_binds": True}))
        result = (await db.execute(query)).all()

        return result

    @staticmethod
    @cache_or_db("posts:by_id", models.Post)
    async def get_by_id(db: AsyncSession, post_id: int) -> models.Post | None:
        """
        Возвращает пост по post_id
        """

        query = (
            select(models.Post)
            .where(models.Post.post_id == post_id)
        )
        result = (await db.execute(query)).scalar_one_or_none()

        return result
    
    @staticmethod
    @cache_or_db("posts:by_id_with_votes", posts.PostResponseWithVotes)
    async def get_by_id_with_votes(db: AsyncSession, post_id: int) -> Row[Tuple[models.Post, int]] | None:
        """
        Возвращает пост по post_id
        """

        query = (
            select(models.Post, func.count(models.Vote.user_id).label("votes"))
            .join(models.Post.user)
            .options(contains_eager(models.Post.user))
            .outerjoin(models.Vote, models.Post.post_id == models.Vote.post_id)
            .where(models.Post.post_id == post_id)
            .group_by(models.Post.post_id, models.User.user_id)
        )
        print(query.compile(compile_kwargs={"literal_binds": True}))
        result = (await db.execute(query)).one_or_none()

        return result

    @staticmethod
    async def create(db: AsyncSession, post_data: dict[str, Any]) -> models.Post:
        """
        Создаёт новый пост
        """

        new_post = models.Post(**post_data)

        db.add(new_post)
        await db.commit()
        await db.refresh(new_post)

        return new_post

    @staticmethod
    async def delete(db: AsyncSession, post_id: int) -> None:
        """
        Удаляет пост
        """
        stmt = (
            delete(models.Post)
            .where(models.Post.post_id == post_id)
        )

        await db.execute(stmt)
        await db.commit()

    @staticmethod
    async def update(db: AsyncSession, post_data: dict[str, Any], post_id: int) -> models.Post:
        """
        Обновляет существующий пост
        """
        stmt = (
            update(models.Post)
            .values(**post_data)
            .where(models.Post.post_id == post_id)
            .returning(models.Post)
        )

        result = (await db.execute(stmt)).scalar_one()
        await db.commit()
        return result

    @staticmethod
    async def get_with_votes_test(db: AsyncSession):
        query = (
            select(models.Post)
            .options(joinedload(models.Post.votes))
        )

        result = (await db.execute(query)).unique().scalars().all()
        return result
    
