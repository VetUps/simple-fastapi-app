from sqlalchemy import select, delete, insert, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload
from pydantic import TypeAdapter
from typing import Any, List

from app import models
from app.redis import cache_or_db
from app.schemas import posts

post_with_votes_adapter = TypeAdapter(posts.PostWithVotes)
post_with_votes_list_adapter = TypeAdapter(List[posts.PostWithVotes])
post_with_user_adapter = TypeAdapter(posts.PostWithUser)
post_without_user_adapter = TypeAdapter(posts.PostWithoutUser)

class PostRepository:
    @staticmethod
    @cache_or_db("posts:many", List[posts.PostWithVotes])
    async def get_many(db: AsyncSession, limit: int = 5, offset: int = 0, search: str = "") -> List[posts.PostWithVotes]:
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
        return post_with_votes_list_adapter.validate_python(result)

    @staticmethod
    @cache_or_db("posts:by_id", posts.PostWithUser)
    async def get_by_id(db: AsyncSession, post_id: int) -> posts.PostWithUser | None:
        """
        Возвращает пост по post_id
        """

        query = (
            select(models.Post)
            .options(joinedload(models.Post.user))
            .where(models.Post.post_id == post_id)
        )
        result = (await db.execute(query)).scalar_one_or_none()

        return post_with_user_adapter.validate_python(result) if result else None
    
    @staticmethod
    @cache_or_db("posts:by_id_with_votes", posts.PostWithVotes)
    async def get_by_id_with_votes(db: AsyncSession, post_id: int) -> posts.PostWithVotes | None:
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

        return post_with_votes_adapter.validate_python(result) if result else None

    @staticmethod
    async def create(db: AsyncSession, post_data: dict[str, Any]) -> posts.PostWithUser:
        """
        Создаёт новый пост
        """
        new_post = models.Post(**post_data)

        db.add(new_post)
        await db.commit()

        return await PostRepository.get_by_id(db, new_post.post_id)

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
    async def update(db: AsyncSession, post_data: dict[str, Any], post_id: int) -> posts.PostWithUser:
        """
        Обновляет существующий пост
        """
        stmt = (
            update(models.Post)
            .values(**post_data)
            .where(models.Post.post_id == post_id)
        )

        await db.execute(stmt)
        await db.commit()

        return await PostRepository.get_by_id(db, post_id)
