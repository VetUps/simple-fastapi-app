from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.posts import PostRepository
from app.schemas import posts
from app import models

class PostService:
    @staticmethod
    async def get_posts(db: AsyncSession, limit: int = 5, page: int = 1, search: str = ""):
        offset = (page - 1) * limit
        return await PostRepository.get_many(db, limit, offset, search)

    @staticmethod
    async def get_post(db: AsyncSession, post_id: int):
        post = await PostRepository.get_by_id_with_votes(db, post_id)

        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {post_id} was not found")
        
        return post

    @staticmethod
    async def create_post(db: AsyncSession, post: posts.PostCreate, current_user: models.User):
        post_data = post.model_dump()
        user_id = current_user.user_id

        post_data["user_id"] = user_id

        return await PostRepository.create(db, post_data)

    @staticmethod
    async def delete_post(db: AsyncSession, post_id: int, current_user: models.User):
        post_to_delete = await PostRepository.get_by_id(db, post_id)

        if post_to_delete is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {post_id} was not found")

        if post_to_delete.user.user_id != current_user.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"not authorized to perform requested action")

        await PostRepository.delete(db, post_id)

    @staticmethod
    async def update_post(db: AsyncSession, post_id: int, post: posts.PostUpdate, current_user: models.User):
        post_to_update = await PostRepository.get_by_id(db, post_id)

        if post_to_update is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {post_id} was not found")

        if post_to_update.user.user_id != current_user.user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"not authorized to perform requested action")

        post_data = post.model_dump()
        updated_post = await PostRepository.update(db, post_data, post_id)

        return updated_post
    