from sqlalchemy.orm import Session
from pwdlib import PasswordHash
from typing import Any

from . import models


password_hasher = PasswordHash.recommended()

def hash_password(password: str) -> Any:
    return password_hasher.hash(password)

def verify(plain_password: str, real_password: str) -> bool:
    return password_hasher.verify(plain_password, real_password)

def find_user(db: Session, user_email: str) -> models.User | None:
    return db.query(models.User).where(models.User.user_email == user_email).first()

def auth_user(db: Session, user_email: str, user_password: str) -> models.User | None:
    user = find_user(db, user_email)

    if user is None:
        return

    if verify(user_password, user.user_password):
        return user
