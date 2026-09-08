from sqlalchemy.orm import Session
from sqlalchemy import select

from app import models

class UserRepository:
    @staticmethod
    def get_many(db: Session, limit: int = 5, offset: int = 0, search: str = ""):
        query = (
            select(models.User)
            .where(models.User.user_email.contains(search))
            .limit(limit)
            .offset(offset)
        )

        result = db.execute(query).all()
        return result

    @staticmethod
    def get_by_id(db: Session, user_id: int):
        query = (
            select(models.User)
            .where(models.User.user_id == user_id)
        )

        result = db.execute(query).one_or_none()
        return result

    @staticmethod
    def get_by_email(db: Session, user_email: str):
        query = (
            select(models.User)
            .where(models.User.user_email == user_email)
        )

        result = db.execute(query).scalar_one_or_none()
        return result

    @staticmethod
    def craete(db: Session, user_data: dict):
        new_user = models.User(**user_data)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user