from fastapi import status, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.users import UserService
from app.schemas import users, posts
from app.utils import rate_limit

router = APIRouter(
    prefix="/users",
    tags=["Users"]
    )

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=users.UserResponse, dependencies=[Depends(rate_limit(5, 60))])
async def create_user(user: users.UserCreate, db: AsyncSession = Depends(get_db)):
    return await UserService.create_user(db, user)

@router.get("/{id}", response_model=users.UserResponse | posts.UserWithPosts, dependencies=[Depends(rate_limit(120, 60))])
async def get_user(id: int, include: str = "", db: AsyncSession = Depends(get_db)):
    if include == "posts":
        return await UserService.get_user_with_posts(db, id)
    return await UserService.get_user_by_id(db, id)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(rate_limit(5, 60))])
async def delete_user(id: int, db: AsyncSession = Depends(get_db)):
    await UserService.delete_user(db, id)
