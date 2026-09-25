from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.posts import PostRepository
from app.repositories.votes import VoteRepository
from app.schemas import users

class VoteService:
    @staticmethod
    async def vote_post(db: AsyncSession, post_id: int, current_user: users.UserResponse):
        user_id = current_user.user_id
        post = await PostRepository.get_by_id(db, post_id)

        if post is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {post_id} was not found")

        existed_vote = await VoteRepository.get_by_user_post_id(db, post_id, user_id)

        if existed_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user {current_user.user_id} already vote on post {post_id}")

        vote = await VoteRepository.create(db, post_id, user_id)
        return vote

    @staticmethod
    async def unvote_post(db: AsyncSession, post_id: int, current_user: users.UserResponse):
        user_id = current_user.user_id
        post = await PostRepository.get_by_id(db, post_id)
        
        if post is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {post_id} was not found")

        existed_vote = await VoteRepository.get_by_user_post_id(db, post_id, user_id)
        
        if existed_vote is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"vote not found")

        await VoteRepository.delete(db, post_id, user_id)