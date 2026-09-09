from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.repositories.users import UserRepository
from app.config import settings
from app import schemas, models, security, oauth2


class UserService:
    @staticmethod
    def create_user(db: Session, user: schemas.users.UserCreate):
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

    @staticmethod
    def auth_user(db: Session, user_data: OAuth2PasswordRequestForm):
        user = UserRepository.get_by_email(db, user_data.username)

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="invalid credentials")

        if not security.verify(user_data.password, user.user_password):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="invalid credentials")

        token = oauth2.create_access_token(
            data={
                "user_id": user.user_id,
                "user_email": user.user_email
                },
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return {
            "access_token": token,
            "token_type": "Bearer"
        }