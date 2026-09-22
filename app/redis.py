import redis.asyncio as aioredios
from app.config import settings

redis_client = aioredios.Redis(
    host=settings.REDIS_HOST, 
    port=settings.REDIS_PORT, 
    db=0, 
    decode_responses=True # При = True будет возвращать строки, а не байты
)

async def invalidate_posts_cache():
    cursor = 0

    while True:
        cursor, keys = await redis_client.scan(cursor=cursor, match="posts:*", count=100)

        if keys:
            await redis_client.delete(*keys)
        if cursor == 0:
            break