from pwdlib import PasswordHash
from typing import Any

password_hasher = PasswordHash.recommended()

def hash_password(password: str) -> Any:
    return password_hasher.hash(password)

def verify(plain_password: str, real_password: str) -> bool:
    return password_hasher.verify(plain_password, real_password)