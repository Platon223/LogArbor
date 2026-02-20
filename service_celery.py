from flask import Flask
from dotenv import load_dotenv
import os
from extensions.mongo import mongo

def create_celery_app():

    load_dotenv()

    app = Flask(__name__)

    app.config["MONGO_URI"] = os.getenv("MONGO")

    mongo.init_app(app)

    return app

app = create_celery_app()