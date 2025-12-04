from flask import Flask, request, Response
from dotenv import load_dotenv
import os
from datetime import timedelta
from extensions.mongo import mongo
from logg.log import setup
import logging

load_dotenv()

def create_service():
    app = Flask(__name__)
    setup()
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    app.config["MONGO_URI"] = os.getenv("MONGO")
    app.secret_key = os.getenv("APP_SECRET")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=10)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(hours=24)

    mongo.init_app(app)

    from blueprints.auth.routes import auth_bl
    
    app.register_blueprint(auth_bl, url_prefix='/auth')


    return app


