from fastapi import Depends, APIRouter, Response, Cookie, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.database import get_db
from app.services.users import UserService
from app.schemas import tokens
from app.config import settings
from app.utils import rate_limit

router = APIRouter(
    tags=["Auth"],
    prefix="/auth"
)

@router.post("/login", response_model=tokens.AccessToken, dependencies=[Depends(rate_limit(5, 60))])
async def login(response: Response, user: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    access_token, refresh_token = await UserService.auth_user(db, user)

    # Установка refresh токена в куки для защиты от XSS-атак
    response.set_cookie(
        key="refresh_token", # имя куки
        value=refresh_token, # сам токен
        httponly=True, # невозможность прочитать токен JS-у
        secure=False, # передача только по HTTPS
        samesite="lax", # защита от CSRF-атак
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60, # время жизни в секундах
        path="/auth/" # на какой адрес бразуер будет прикреплять эту куку
    )

    return {
        "access_token": access_token,
        "token_type": "Bearer"
    }

@router.post("/refresh", response_model=tokens.AccessToken, dependencies=[Depends(rate_limit(5, 60))])
async def refresh(response: Response, refresh_token: Annotated[str | None, Cookie()] = None, db: AsyncSession = Depends(get_db)):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")

    access_token, refresh_token = await UserService.refresh_user_tokens(db, refresh_token)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        path="/auth/"
    )

    return {
        "access_token": access_token,
        "token_type": "Bearer"
    }

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(rate_limit(5, 60))])
async def logout(refresh_token: Annotated[str | None, Cookie()] = None, db: AsyncSession = Depends(get_db)):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")

    await UserService.logout_user(db, refresh_token)
