from flask import Blueprint, request, g, render_template
from handlers.auth_check_wrapper import auth_check_wrapper
from pymongo.errors import OperationFailure, PyMongoError
from log_arbor.utils import log
import os
from dotenv import load_dotenv
from extensions.mongo import mongo

load_dotenv(dotenv_path='../../.env')

settings_bl = Blueprint("settings_bl", __name__, template_folder="templates", static_folder="static")

@settings_bl.app_errorhandler(OperationFailure)
def handle_operation_failure(e):
    try:
        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "critical", f"failed db operation at: {request.path} and error: {str(e)}")
    except Exception as loge:
        return {"message": f"{loge}"}, 500
    return {"message": "something went wrong"}, 500

@settings_bl.app_errorhandler(PyMongoError)
def handle_operation_failure_pymongo(e):
    try:
        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "critical", f"failed db operation at: {request.path} and error: {str(e)} because of a pymongo error")
    except Exception as loge:
        return {"message": f"{loge}"}, 500
    return {"message": "something went wrong"}, 500

@settings_bl.app_errorhandler(Exception)
def handle_operation_failure_exception(e):
    try:
        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "critical", f"failed at: {request.path} and error: {str(e)}")
    except Exception as loge:
        return {"message": f"{loge}"}, 500
    return {"message": "something went wrong"}, 500

@settings_bl.route("/", methods=["GET"])
def settings_page():
    if not request.blueprint == "settings_bl":
        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "warning", f"ui route: /, was accessed with non ui blueprint: {request.path}")
        return {"message": "ui route only"}, 404

    return render_template("settings.html")

@settings_bl.route("/settings", methods=["GET"])
@auth_check_wrapper()
def settings_info():
    if not request.blueprint == "settings_api":
        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "warning", f"api route: /settings, was accessed with non api blueprint: {request.path}")
        return {"message": "api route only"}, 404
    
    current_user = mongo.db.users.find_one({"id": getattr(request, "auth_identity", None)})

    if not current_user:
        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "warning", "user not found at /settings/settings (GET)")
        return {"message": "user not found"}, 404
    
    oauth_providers = ["Github User", "Google User"]
    
    settings_object = {
        "id": current_user["id"],
        "username": current_user["username"],
        "email": current_user["email"],
        "account_type": current_user["account_type"],
        "auth_provider": "LogArbor" if not current_user["password"] in oauth_providers else current_user["password"]
    }

    return {"message": settings_object}, 200
    


