from sqlalchemy import select, exists, update
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import TypeAdapter
from datetime import datetime

from app import models
from app.schemas import tokens

refresh_token_adapter = TypeAdapter(tokens.RefreshToken)
refresh_token_with_user_adapter = TypeAdapter(tokens.RefreshTokenWithUser)

class RefreshTokenRepository:
    @staticmethod
    async def get_by_hash(db: AsyncSession, token_hash: str) -> tokens.RefreshTokenWithUser | None:
        query = (
            select(models.RefreshToken)
            .options(joinedload(models.RefreshToken.user))
            .where(models.RefreshToken.token_hash == token_hash)
        )

        result = (await db.execute(query)).scalar_one_or_none()
        return refresh_token_with_user_adapter.validate_python(result) if result else None

    @staticmethod
    async def create(db: AsyncSession, token_hash: str, user_id: int, expires_at: datetime) -> tokens.RefreshToken:
        new_token = models.RefreshToken(token_hash=token_hash, user_id=user_id, expires_at=expires_at)

        db.add(new_token)
        await db.commit()
        await db.refresh(new_token)

        return refresh_token_adapter.validate_python(new_token)

    @staticmethod
    async def revoke(db: AsyncSession, token_id: int):
        stmt = (
            update(models.RefreshToken)
            .where(models.RefreshToken.token_id == token_id)
            .values(is_revoked=True)
        )

        await db.execute(stmt)
        await db.commit()

    @staticmethod
    async def revoke_tokens_by_user_id(db: AsyncSession, user_id: int):
        stmt = (
            update(models.RefreshToken)
            .where(models.RefreshToken.user_id == user_id)
            .values(is_revoked=True)
        )

        await db.execute(stmt)
        await db.commit()
