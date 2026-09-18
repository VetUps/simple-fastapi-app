from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.repositories.users import UserRepository
from app.schemas import users
from app.config import settings
from app import security, oauth2


class UserService:
    @staticmethod
    async def create_user(db: AsyncSession, user: users.UserCreate):
        user_data = user.model_dump()
        existed_user = await UserRepository.get_by_email(db, user.user_email)

        if existed_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user with email {user.user_email} already exist")

        user_data["user_password"] = await security.hash_password(user_data["user_password"])
        new_user = await UserRepository.craete(db, user_data)
        return new_user

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int):
        user = await UserRepository.get_by_id(db, user_id)

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id {user_id} was not found")

        return user

    @staticmethod
    async def get_user_by_email(db: AsyncSession, user_email: str):
        user = await UserRepository.get_by_email(db, user_email)

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id {user_email} was not found")

        return user   

    @staticmethod
    async def get_user_with_posts(db: AsyncSession, user_id: int):
        user = await UserRepository.get_user_by_id_with_posts(db, user_id)

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id {user_id} was not found")

        return user

    @staticmethod
    async def auth_user(db: AsyncSession, user_data: OAuth2PasswordRequestForm):
        user = await UserRepository.get_by_email(db, user_data.username)
        print(user_data.username)

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

        if not await security.verify(user_data.password, user.user_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

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

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int):
        await UserService.get_user_by_id(db, user_id)
        await UserRepository.delete(db, user_id)
        