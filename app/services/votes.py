from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.posts import PostRepository
from app.repositories.votes import VoteRepository
from app import models

class VoteService:
    @staticmethod
    def vote_post(db: Session, post_id: int, current_user: models.User):
        user_id = current_user.user_id
        post = PostRepository.get_by_id(db, post_id)

        if post is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {post_id} was not found")

        existed_vote = VoteRepository.get_by_user_post_id(db, post_id, user_id)

        if existed_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user {current_user.user_id} already vote on post {post_id}")

        vote = VoteRepository.create(db, post_id, user_id)
        return vote

    @staticmethod
    def unvote_post(db: Session, post_id: int, current_user: models.User):
        user_id = current_user.user_id
        post = PostRepository.get_by_id(db, post_id)
        
        if post is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {post_id} was not found")

        existed_vote = VoteRepository.get_by_user_post_id(db, post_id, user_id)
        
        if existed_vote is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"vote not found")

        VoteRepository.delete(db, post_id, user_id)