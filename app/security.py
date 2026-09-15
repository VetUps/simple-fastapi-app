from pwdlib import PasswordHash
import asyncio

password_hasher = PasswordHash.recommended()

async def hash_password(password: str) -> str:
    return await asyncio.to_thread(password_hasher.hash, password)

async def verify(plain_password: str, real_password: str) -> bool:
    return await asyncio.to_thread(password_hasher.verify, password=plain_password, hash=real_password)
