from celery import Celery
import os

def create_celery():
    redis_url = "redis://localhost:6379/0"

    celery = Celery(
        "logarbor",
        broker=redis_url,
        backend=redis_url
    )

    celery.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )

    return celery

celery = create_celery()
