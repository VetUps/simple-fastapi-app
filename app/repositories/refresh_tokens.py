from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import TypeAdapter
from datetime import datetime

from app import models
from app.schemas import tokens

refresh_token_adapter = TypeAdapter(tokens.RefreshToken)

class RefreshTokenRepository:
    @staticmethod
    async def get_by_hash(db: AsyncSession, token_hash: str) -> tokens.RefreshToken:
        query = (
            select(models.RefreshToken)
            .where(models.RefreshToken.token_hash == token_hash)
        )

        result = (await db.execute(query)).scalar_one()
        return refresh_token_adapter.validate_python(result)

    @staticmethod
    async def create(db: AsyncSession, token_hash: str, user_id: int, expires_at: datetime) -> tokens.RefreshToken:
        new_token = models.RefreshToken(token_hash=token_hash, user_id=user_id, expires_at=expires_at)

        db.add(new_token)
        await db.commit()
        await db.refresh(new_token)

        return refresh_token_adapter.validate_python(new_token)

    @staticmethod
    async def is_exists(db: AsyncSession, token_hash: str) -> bool:
        query = select(
            exists(
                select(models.RefreshToken)
                .where(models.RefreshToken.token_hash == token_hash)
            )
        )

        result = (await db.execute(query)).scalar_one()
        return result
    