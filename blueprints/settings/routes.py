from flask import Blueprint, request, g, render_template
from handlers.auth_check_wrapper import auth_check_wrapper
from pymongo.errors import OperationFailure, PyMongoError
from log_arbor.utils import log
import os
from extensions.mongo import mongo
from validates.validate_api import validate_route
from domains.service import check_ui_blueprint, check_api_blueprint
from domains.settings.service import get_settings, account_deletion, request_account_deletion

settings_bl = Blueprint("settings_bl", __name__, template_folder="templates", static_folder="static")

@settings_bl.app_errorhandler(OperationFailure)
def handle_operation_failure(e):

    try:

        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "critical", f"failed db operation at: {request.path} and error: {str(e)}", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")
    except Exception as loge:

        return {"message": f"{loge}"}, 500
    
    return {"message": "something went wrong"}, 500





@settings_bl.app_errorhandler(PyMongoError)
def handle_operation_failure_pymongo(e):

    try:

        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "critical", f"failed db operation at: {request.path} and error: {str(e)} because of a pymongo error", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")
    except Exception as loge:

        return {"message": f"{loge}"}, 500
    
    return {"message": "something went wrong"}, 500





@settings_bl.app_errorhandler(Exception)
def handle_operation_failure_exception(e):

    try:

        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "critical", f"failed at: {request.path} and error: {str(e)}", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")
    except Exception as loge:

        return {"message": f"{loge}"}, 500
    
    return {"message": f"something went wrong"}, 500





@settings_bl.before_request
def data_validation():

    allowed_http_methods = ["POST", "DELETE"]
    
    if request.method in allowed_http_methods and request.path != "/api/v1/settings/account":

        path = request.path

        data = validate_route(request, path.removeprefix("/api/v1"))

        if "error" in data:
            log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "error", f"failed api validation on: {request.path} with error: {data}", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")
            return {"message": data}, 400
        
        g.data = data





@settings_bl.route("/", methods=["GET"])
def settings_page():
    
    # Checks ui blueprint

    check = check_ui_blueprint(request.blueprint, "settings_bl")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "warning", f"ui route was accessed with non ui blueprint: {request.path}", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")

        return {"message": check["message"]}, 404
    

    # Renders settings.html

    return render_template("settings.html")





@settings_bl.route("/settings", methods=["GET"])
@auth_check_wrapper()
def settings_info():

    # Checks api blueprint

    check = check_api_blueprint(request.blueprint, "settings_api")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")

        return {"message": check["message"]}, 404
    

    # Gets settings    
    
    settings = get_settings(getattr(request, "auth_identity", None), mongo.db.users, request)

    if not settings["ok"]:

        return {"message": settings["message"]}, settings["status"]
    else:

        return {"message": settings["message"]}, 200
    




@settings_bl.route("/account", methods=["DELETE"])
@auth_check_wrapper()
def delete_account():

    # Checks api blueprint

    check = check_api_blueprint("SETTINGS", request.blueprint, "settings_api", request)

    if not check["ok"]:

        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")

        return {"message": check["message"]}, 404
    

    # Sends a request to delete an account

    request_delete_email = request_account_deletion(getattr(request, "auth_identity", None), mongo.db.users, request)

    if not request_delete_email["ok"]:

        return {"message": request_delete_email["message"]}, request_delete_email["status"]
    else:

        return {"message": request_delete_email["message"]}, 200
    




@settings_bl.route("/account_approve", methods=["DELETE"])
def approve_account_deletion():

    # Checks api blueprint
    
    check = check_api_blueprint("SETTINGS", request.blueprint, "settings_api", request)

    if not check["ok"]:

        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")

        return {"message": check["message"]}, 404
    

    # Deletes an account

    delete_account_approve = account_deletion(g.data.get("account_id"), mongo.db.users, g.data, request)

    if not delete_account_approve["ok"]:

        return {"message": delete_account_approve["message"]}, delete_account_approve["status"]
    else:

        return {"message": delete_account_approve["message"]}, 200