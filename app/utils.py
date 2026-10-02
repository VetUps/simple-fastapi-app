import asyncio
from app.redis import redis_client
from fastapi import HTTPException, status, Request

async def send_notification(post_id: int, author_email: str) -> None:
    print(f"[notify] Отправка уведомления для поста {post_id}")
    await asyncio.sleep(3)
    print(f"[notify] Уведомление о создании поста {post_id} отправленя для {author_email}")


async def check_rate_limit(key:str, limit: int, window: int):
    current = await redis_client.incr(key)

    if current == 1:
        await redis_client.expire(key, time=window)

    if current > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later."
        )

def rate_limit(limit: int, window: int):
    async def dependency(request: Request):
        client_ip = request.client.host
        endpoint = request.url.path
        key = f"rate_limit:{endpoint}:{client_ip}"

        await check_rate_limit(key, limit, window)

    return dependency