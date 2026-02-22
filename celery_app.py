from celery import Celery
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_celery():
    redis_url =  os.getenv("REDIS_URL_CELERY", "redis://127.0.0.1:6379/0")
    redis_backend_url = os.getenv("REDIS_URL_CELERY_BACKEND", "redis://127.0.0.1:6379/1")
 

    celery = Celery(
        "logarbor",
        broker=redis_url,
        backend=redis_backend_url,
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
