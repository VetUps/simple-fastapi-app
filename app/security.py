from pwdlib import PasswordHash
import asyncio
import hashlib

password_hasher = PasswordHash.recommended()

async def hash_password(password: str) -> str:
    return await asyncio.to_thread(password_hasher.hash, password)

async def verify(plain_password: str, real_password: str) -> bool:
    return await asyncio.to_thread(password_hasher.verify, password=plain_password, hash=real_password)

def hash_refresh_token(refresh_token: str) -> str:
    token_encoded = refresh_token.encode('utf-8')
    token_hashed = hashlib.sha256(token_encoded).hexdigest()

    return token_hashed
