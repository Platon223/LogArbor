from celery import Celery
import os

def create_celery():
    redis_url =  os.getenv("REDIS_URL_CELERY", "redis://127.0.0.1:6379/0")

    celery = Celery(
        "logarbor",
        broker="redis://127.0.0.1:6379/0",
        backend="redis://127.0.0.1:6379/1",
        include=["tasks.add_log_api_task"]
    )

    celery.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        broker_connection_retry_on_startup=True, 
        broker_transport_options={'max_retries': 1},
    )

    return celery

celery = create_celery()
