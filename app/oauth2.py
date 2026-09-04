from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from . import schemas

import datetime
from datetime import timedelta

import jwt
from jwt.exceptions import InvalidTokenError

ouath2_schema = OAuth2PasswordBearer(tokenUrl="login")

# Потом перегенерирую и уберу в .env :D
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def verify_access_token(token: str, credentials_exception: HTTPException):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithm=ALGORITHM)

        user_id = payload.get("user_id")
        user_email = payload.get("user_email")

        if user_id is None or user_email is None:
            raise credentials_exception
        token_data = schemas.TokenData(**payload)

        return token_data
    except InvalidTokenError:
        raise credentials_exception

def get_current_user(token: str = Depends(ouath2_schema)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn`t validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
        )

    return verify_access_token(token, credentials_exception)