import asyncio

async def send_notification(post_id: int, author_email: str) -> None:
    print(f"[notify] Отправка уведомления для поста {post_id}")
    await asyncio.sleep(3)
    print(f"[notify] Уведомление о создании поста {post_id} отправленя для {author_email}")
    