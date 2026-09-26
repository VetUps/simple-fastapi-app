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
        is_exists = await UserRepository.is_exists_by_email(db, user.user_email)

        if is_exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user with email {user.user_email} already exist")

        user_data = user.model_dump()
        user_data["user_password"] = await security.hash_password(user_data["user_password"])
        new_user = await UserRepository.craete(db, user_data)

        return new_user

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int):
        is_exists = await UserRepository.is_exists(db, user_id)

        if not is_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id {user_id} was not found")

        user = await UserRepository.get_by_id(db, user_id)

        return user

    @staticmethod
    async def get_user_by_email(db: AsyncSession, user_email: str):
        is_exists = await UserRepository.is_exists_by_email(db, user_email)

        if not is_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id {user_email} was not found")

        user = await UserRepository.get_by_email(db, user_email)

        return user   

    @staticmethod
    async def get_user_with_posts(db: AsyncSession, user_id: int):
        is_exists = await UserRepository.is_exists(db, user_id)

        if not is_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id {user_id} was not found")

        user = await UserRepository.get_user_by_id_with_posts(db, user_id)

        return user

    @staticmethod
    async def auth_user(db: AsyncSession, user_data: OAuth2PasswordRequestForm):
        is_exists = await UserRepository.is_exists_by_email(db, user_data.username)

        if not is_exists:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

        user = await UserRepository.get_by_email_security(db, user_data.username)

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
        is_exists = await UserRepository.is_exists(db, user_id)

        if not is_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user with id {user_id} was not found")

        await UserRepository.delete(db, user_id)
        