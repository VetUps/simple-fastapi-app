from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.users import UserService
from app.schemas import tokens

router = APIRouter(
    tags=["Auth"]
)

@router.post("/login", response_model=tokens.Token)
async def login(user: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    return await UserService.auth_user(db, user)
