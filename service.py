from flask import Flask, request, Response, jsonify
from dotenv import load_dotenv
import os
from datetime import timedelta
from extensions.mongo import mongo
from extensions.bcrypt import bcrypt
from extensions.jwt import jwt
from extensions.oauth import oauth
from logg.log import setup
import logging

load_dotenv()

def create_service():
    app = Flask(__name__)
    setup()
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    logging.getLogger("pymongo").setLevel(logging.ERROR)
    app.config["MONGO_URI"] = os.getenv("MONGO")
    app.secret_key = os.getenv("APP_SECRET")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=10)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(hours=24)

    mongo.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    oauth.init_app(app)


    app.errorhandler(Exception)
    def catch(e):
        return {"message": "something went wrong on our end"}, 500
    
    @jwt.expired_token_loader
    def expired_access_token(jwt_header, jwt_payload):
        token = jwt_payload.get('type')
        return jsonify({'message': f'{token} token has expired'})
    
    @jwt.invalid_token_loader
    def invalid(callback):
        return jsonify({'message': 'Invalid access token'})
    
    @jwt.unauthorized_loader
    def unauth(callback):
        return jsonify({'message': 'no token provided'})

    from blueprints.auth.routes import auth_bl
    from blueprints.home.routes import home_bl
    
    app.register_blueprint(auth_bl, url_prefix='/auth')
    app.register_blueprint(home_bl, url_prefix='/home')



    return app


