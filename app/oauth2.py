from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import schemas, models, database
from app.config import settings

import datetime
from datetime import timedelta

import jwt
from jwt.exceptions import InvalidTokenError


ouath2_schema = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.datetime.now() + expires_delta
    else:
        expire = datetime.datetime.now() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt

def verify_access_token(token: str, credentials_exception: HTTPException):
    try:
        print(f"{token}")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        user_id = payload.get("user_id")
        user_email = payload.get("user_email")

        if user_id is None or user_email is None:
            raise credentials_exception
        token_data = schemas.tokens.TokenData(**payload)

        return token_data
    except InvalidTokenError as e:
        raise credentials_exception

def get_current_user(token: str = Depends(ouath2_schema), db: Session = Depends(database.get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn`t validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
        )

    token_data = verify_access_token(token, credentials_exception)
    user_id = token_data.user_id

    return db.query(models.User).where(models.User.user_id == user_id).first()