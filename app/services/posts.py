from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.posts import PostRepository
from app import schemas, models

class PostSerivce:
    @staticmethod
    def get_posts(db: Session, limit: int = 5, page: int = 1, search: str = ""):
        offset = (page - 1) * limit
        return PostRepository.get_many(db, limit, offset, search)

    @staticmethod
    def get_post(db: Session, post_id: int):
        post = PostRepository.get_by_id_with_votes(db, post_id)

        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {post_id} was not found")
        
        return post

    @staticmethod
    def create_post(db: Session, post: schemas.PostCreate, current_user: models.User):
        post_data = post.model_dump()
        user_id = current_user.user_id

        post_data["user_id"] = user_id

        return PostRepository.create(db, post_data)

    @staticmethod
    def delete_post(db: Session, post_id: int, current_user: models.User):
        post_to_delete = PostRepository.get_by_id(db, post_id)

        if post_to_delete is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")

        if post_to_delete.user_id != current_user.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"not authorized to perform requested action")

        PostRepository.delete(db, post_id)

    @staticmethod
    def update_post(db: Session, post_id: int, post: schemas.PostUpdate, current_user: models.User):
        post_to_update = PostRepository.get_by_id(db, post_id)

        if post_to_update is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {post_id} was not found")

        if post_to_update.user_id != current_user.user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"not authorized to perform requested action")

        post_data = post.model_dump()
        updated_post = PostRepository.update(db, post_data, post_id)

        return updated_post
    