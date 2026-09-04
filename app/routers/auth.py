from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from ..utils.hashing import verify
from .. import models, schemas
import typing

router = APIRouter(
    prefix="auth",
    tags=["Auth"]
)

@router.post("/")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):

    exist_user = db.query(models.User).where(models.User.user_email == user.user_email).first()

    if exist_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")

    if verify(user.user_password, exist_user.user_password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")