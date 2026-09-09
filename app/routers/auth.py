from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from app.database import get_db
from app.services.users import UserService
from app.schemas import tokens

router = APIRouter(
    tags=["Auth"]
)

@router.post("/login", response_model=tokens.Token)
def login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return UserService.auth_user(db, user)
