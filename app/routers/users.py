from fastapi import status, Depends, APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.users import UserService
from app import schemas

router = APIRouter(
    prefix="/users",
    tags=["Users"]
    )

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return UserService.create_user(db, user)

@router.get("/{id}", response_model=schemas.UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    return UserService.get_user(db, id)