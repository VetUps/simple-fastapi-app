from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

import datetime
from datetime import timedelta
from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError

from app.database import get_db
from app.schemas import tokens, users
from app.config import settings
from app.services.users import UserService


ouath2_schema = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.datetime.now() + expires_delta
    else:
        expire = datetime.datetime.now() + timedelta(minutes=15)

    to_encode.update(
        {
            "exp": expire,
            "type": "access"
        }
    )
    access_token = jwt.encode(to_encode, key=settings.ACCESS_TOKEN_SECRET, algorithm=settings.ALGORITHM) # type: ignore

    return access_token

def create_refresh_token(expires_delta: timedelta | None = None):
    if expires_delta:
        expire = datetime.datetime.now() + expires_delta
    else:
        expire = datetime.datetime.now() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "exp": expire,
        "type": "refresh"
    }
    refresh_token = jwt.encode(to_encode, key=settings.REFRESH_TOKEN_SECRET, algorithm=settings.ALGORITHM)  # type: ignore

    return refresh_token, expire

def verify_access_token(access_token: str):
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Couldn`t validate credentials", 
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]) # type: ignore

        user_id = payload.get("user_id")
        user_email = payload.get("user_email")
        token_type = payload.get("type")

        if token_type != "access":
            raise exception

        if user_id is None or user_email is None:
            raise exception
        token_data = tokens.AccessTokenData(**payload)

        return token_data
    except InvalidTokenError:
        raise exception

def verify_refresh_token(refresh_token: str):
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="The provided refresh token is invalid, expired, or revoked."
    )

    try:
        payload = jwt.decode(refresh_token, key=settings.REFRESH_TOKEN_SECRET, algorithms=[settings.ALGORITHM]) # type: ignore

        token_type = payload.get("type")

        if token_type != "refresh":
            raise exception
    except InvalidTokenError:
        raise exception


async def get_current_user(token: str = Depends(ouath2_schema), db: AsyncSession = Depends(get_db)) -> users.UserResponse:
    token_data = verify_access_token(token)
    user_id = token_data.user_id

    current_user = await UserService.get_user_by_id(db, user_id)

    return current_user