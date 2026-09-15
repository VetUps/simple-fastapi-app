from fastapi import status, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.users import UserService
from app.schemas import users

router = APIRouter(
    prefix="/users",
    tags=["Users"]
    )

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=users.UserResponse)
async def create_user(user: users.UserCreate, db: AsyncSession = Depends(get_db)):
    return await UserService.create_user(db, user)

@router.get("/{id}", response_model=users.UserResponse)
async def get_user(id: int, db: AsyncSession = Depends(get_db)):
    return await UserService.get_user(db, id)
