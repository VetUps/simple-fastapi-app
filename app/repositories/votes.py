from sqlalchemy import select, insert, delete
from sqlalchemy.orm import Session

from app import models

class VoteRepository:
    @staticmethod
    def get_by_user_post_id(db: Session, post_id: int, user_id: int):
        stmt = (
            select(models.Vote)
            .where(models.Vote.post_id == post_id, models.Vote.user_id == user_id)
        )
        result = db.execute(stmt).scalar_one_or_none()

        return result

    @staticmethod
    def create(db: Session, post_id: int, user_id: int):
        stmt = (
            insert(models.Vote)
            .values(post_id=post_id, user_id=user_id)
            .returning(models.Vote)
        )

        result = db.execute(stmt).scalar_one_or_none()
        db.commit()

        return result

    @staticmethod
    def delete(db: Session, post_id: int, user_id: int):
        stmt = (
            delete(models.Vote)
            .where(models.Vote.post_id == post_id, models.Vote.user_id == user_id)
        )

        db.execute(stmt)
        db.commit()
