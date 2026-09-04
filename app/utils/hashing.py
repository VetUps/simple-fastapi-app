from pwdlib import PasswordHash
from typing import Any

password_hasher = PasswordHash.recommended()

def hash_password(password: str) -> Any:
    return password_hasher.hash(password)