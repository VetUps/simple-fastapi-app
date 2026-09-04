from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm, oauth2, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..database import get_db
from ..utils import auth_user
from ..oauth2 import create_access_token
from .. import models, schemas
import typing

router = APIRouter(
    tags=["Auth"]
)

@router.post("/login", response_model=schemas.Token)
def login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    authicated_user = auth_user(db, user.username, user.password)

    if authicated_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")

    acces_token = create_access_token(
        {
            "user_id": authicated_user.user_id,
            "user_email": authicated_user.user_email,
        }
    )

    return {
        "access_token": acces_token,
        "token_type": "Bearer",
        }
