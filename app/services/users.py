from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.users import UserRepository
from app import schemas, models


class UserService:
    @staticmethod
    def create_user(db: Session, user: schemas.UserCreate):
        user_data = user.model_dump()
        existed_user = UserRepository.get_by_email(user.user_email)

        if existed_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user with email {user.user_email} already exist")

        new_user = models.User(**user_data)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    @staticmethod
    def get_user(db: Session, user_id: int):
        user = UserRepository.get_by_id(db, user_id)

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id {user_id} was not found")

        return user