from flask import request, make_response, Blueprint, render_template
from flask_jwt_extended import jwt_required
from handlers.auth_check_wrapper import auth_check_wrapper
from pymongo.errors import DuplicateKeyError, OperationFailure, PyMongoError
from extensions.mongo import mongo
from log_arbor.utils import log
import os
from domains.service import check_api_blueprint, check_ui_blueprint
from domains.home.service import get_credentials

home_blp = Blueprint("home_blp", __name__, template_folder="templates", static_folder="static")

@home_blp.app_errorhandler(OperationFailure)
def handle_operation_failure(e):

    try:
        log(os.getenv("LOGARBOR_HOME_SERVICE_ID"), "critical", f"failed db operation at: {request.path} and error: {str(e)}", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")
    except Exception as loge:

        return {"message": f"{loge}"}, 500
    
    return {"message": "something went wrong"}, 500





@home_blp.app_errorhandler(PyMongoError)
def handle_operation_failure_pymongo(e):

    try:

        log(os.getenv("LOGARBOR_HOME_SERVICE_ID"), "critical", f"failed db operation at: {request.path} and error: {str(e)} because of a pymongo error", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")
    except Exception as loge:

        return {"message": f"{loge}"}, 500
    
    return {"message": "something went wrong"}, 500





@home_blp.app_errorhandler(Exception)
def handle_operation_failure_exception(e):
    try:

        log(os.getenv("LOGARBOR_HOME_SERVICE_ID"), "critical", f"failed at: {request.path} and error: {str(e)}", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")
    except Exception as loge:

        return {"message": f"{loge}"}, 500
    
    return {"message": "something went wrong"}, 500





@home_blp.route("/dashboard", methods=["GET"])
def dashboard():

    # Checks ui blueprint

    check = check_ui_blueprint(request.blueprint, "home_blp")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_HOME_SERVICE_ID"), "warning", f"ui route was accessed with non ui blueprint: {request.path}", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")

        return {"message": check["message"]}, 404
    
    # Renders dashboard.html

    return render_template("dashboard.html")





@home_blp.route("/credentials/username", methods=["POST"])
@auth_check_wrapper()
def username_info():

    # Checks api blueprint

    check = check_api_blueprint(request.blueprint, "home_api")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_HOME_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")

        return {"message": check["message"]}, 404
    
    # Gets user's username

    username_result = get_credentials(mongo.db.users, request)

    if not username_result["ok"]:

        return {"message": username_result["message"]}, username_result["status"]
    
    return {"message": username_result["message"]}, 200


