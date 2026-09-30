from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.repositories.users import UserRepository
from app.repositories.refresh_tokens import RefreshTokenRepository
from app.schemas import users, tokens
from app.config import settings
from app.enums import RevokeReason
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
    async def auth_user(db: AsyncSession, user_data: OAuth2PasswordRequestForm) -> tuple[str, str]:
        user = await UserRepository.get_by_email_security(db, user_data.username)

        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

        if not await security.verify(user_data.password, user.user_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

        return await UserService._issue_token_pair(db, user.user_id, user.user_email)

    @staticmethod
    async def refresh_user_tokens(db: AsyncSession, refresh_token: str) -> tuple[str, str]:
        real_refresh_token = await UserService._validate_refresh_token(db, refresh_token)
        if real_refresh_token.revoke_reason == RevokeReason.USER_LOGOUT:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The provided refresh token is invalid, expired, or revoked.")

        await RefreshTokenRepository.revoke(db, real_refresh_token.token_id, RevokeReason.ROTATED)

        user = real_refresh_token.user
        return await UserService._issue_token_pair(db, user.user_id, user.user_email)

    @staticmethod
    async def logout_user(db: AsyncSession, refresh_token: str):
        real_refresh_token = await UserService._validate_refresh_token(db, refresh_token)
        if real_refresh_token.revoke_reason == RevokeReason.USER_LOGOUT:
            return
        
        await RefreshTokenRepository.revoke(db, real_refresh_token.token_id, RevokeReason.USER_LOGOUT)

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int):
        is_exists = await UserRepository.is_exists(db, user_id)

        if not is_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id {user_id} was not found")

        await UserRepository.delete(db, user_id)

    @staticmethod
    async def _issue_token_pair(db: AsyncSession, user_id: int, user_email: str) -> tuple[str, str]:
        access_token = oauth2.create_access_token(
            data={
                "user_id": user_id,
                "user_email": user_email
                },
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        refresh_token, expire_at = oauth2.create_refresh_token(
            expires_delta=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token_hash = security.hash_refresh_token(refresh_token)
        await RefreshTokenRepository.create(db, refresh_token_hash, user_id, expire_at)

        return access_token, refresh_token

    @staticmethod
    async def _validate_refresh_token(db: AsyncSession, refresh_token: str) -> tokens.RefreshTokenWithUser:
        oauth2.verify_refresh_token(refresh_token)

        refresh_token_hash = security.hash_refresh_token(refresh_token)
        real_refresh_token = await RefreshTokenRepository.get_by_hash(db, refresh_token_hash)

        if real_refresh_token is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The provided refresh token is invalid, expired, or revoked.")


        if real_refresh_token.is_revoked:
            if real_refresh_token.revoke_reason == RevokeReason.ROTATED:
                await RefreshTokenRepository.revoke_tokens_by_user_id(db, real_refresh_token.user_id, RevokeReason.FORCE_LOGOUT)
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The provided refresh token is invalid, expired, or revoked.")

            if real_refresh_token.revoke_reason == RevokeReason.FORCE_LOGOUT:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The provided refresh token is invalid, expired, or revoked.")
        
        return real_refresh_token
    