from celery_app import celery
import os
from domains.logs.service import write_log

# Defines a task to handle log ingestion without blocking user's request

@celery.task
def add_log_task(global_data, services_collection, logs_collection, alerts_collection, users_collection, request):

    return write_log(global_data, services_collection, logs_collection, alerts_collection, users_collection, request)