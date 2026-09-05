from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from datetime import timedelta

from app.database import get_db
from app.utils import auth_user
from app.oauth2 import create_access_token
from app.config import settings
from app import schemas

router = APIRouter(
    tags=["Auth"]
)

@router.post("/login", response_model=schemas.Token)
def login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    authicated_user = auth_user(db, user.username, user.password)

    if authicated_user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

    acces_token = create_access_token(
        {
            "user_id": authicated_user.user_id,
            "user_email": authicated_user.user_email,
        },
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": acces_token,
        "token_type": "Bearer",
        }
