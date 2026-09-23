from celery import Celery
import time

from app.config import settings

celery_app = Celery(
    "app.tasks", # Имя под которым будут регистрироваться задачи
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_BROKER_DB}", # Брокер сообщений
    # backend = url - куда будут приходить резлуьтаты задач
)

celery_app.conf.update(
    task_serializer="json", # сериализация аргументов задач
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
)

@celery_app.task(bind=True, max_retries=3, default_retray_delay=5)
def send_notification(self, post_id: int, author_email: str):
    try:
        print(f"[notify] Отправка уведомления для поста {post_id}")
        time.sleep(3)
        print(f"[notify] Уведомление о создании поста {post_id} отправленя для {author_email}")
    except Exception as e:
        raise self.retry(exc=e)
