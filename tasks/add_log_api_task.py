from celery_app import celery
import os
from domains.logs.service import write_log

# Defines a task to handle log ingestion without blocking user's request

@celery.task
def add_log_task(global_data):

    from service_celery import app
    from extensions.mongo import mongo

    with app.app_context():

        return write_log(global_data, mongo.db.services, mongo.db.logs, mongo.db.alerts, mongo.db.users, mongo.db.windows)
