from flask import request, make_response, Blueprint, render_template
from flask_jwt_extended import jwt_required
from handlers.auth_check_wrapper import auth_check_wrapper
from pymongo.errors import DuplicateKeyError, OperationFailure, PyMongoError
from logg.log import log
from extensions.mongo import mongo
from log_arbor.utils import log as loggg
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')

home_blp = Blueprint("home_blp", __name__, template_folder="templates", static_folder="static")

@home_blp.app_errorhandler(OperationFailure)
def handle_operation_failure(e):
    loggg(os.getenv("LOGARBOR_HOME_SERVICE_ID"), "critical", f"failed db operation at: {request.path} and error: {str(e)}")
    return {"message": "something went wrong"}, 500

@home_blp.app_errorhandler(PyMongoError)
def handle_operation_failure(e):
    loggg(os.getenv("LOGARBOR_HOME_SERVICE_ID"), "critical", f"failed db operation at: {request.path} and error: {str(e)} because of a pymongo error")
    return {"message": "something went wrong"}, 500

@home_blp.app_errorhandler(Exception)
def handle_operation_failure(e):
    loggg(os.getenv("LOGARBOR_HOME_SERVICE_ID"), "critical", f"failed at: {request.path} and error: {str(e)}")
    return {"message": "something went wrong"}, 500

@home_blp.route("/dashboard", methods=["GET"])
def dashboard():
    if not request.blueprint == "home_blp":
        loggg(os.getenv("LOGARBOR_HOME_SERVICE_ID"), "warning", f"ui route: /dashboard, was accessed with non ui blueprint: {request.path}")
        return {"message": "ui route only"}, 404

    return render_template("dashboard.html")


@home_blp.route("/credentials/username", methods=["POST"])
@auth_check_wrapper()
def username_info():
    if not request.blueprint == "home_api":
        loggg(os.getenv("LOGARBOR_HOME_SERVICE_ID"), "warning", f"api route: /credentials/username, was accessed with non api blueprint: {request.path}")
        return {"message": "api route only"}, 404

    user_identity = getattr(request, "auth_identity", None)

    current_user = mongo.db.users.find_one({"id": user_identity})
    
    if not current_user:
        log("DASHBOARD", "warning", "user was not found at credentials/username")
        return {"message": "user not found"}, 404
    
    loggg("e2e48ac7-0913-4d47-b061-0ca4e8ab4a1a", "info", "user got their credentials successufully")
    return {"message": current_user["username"]}, 200


