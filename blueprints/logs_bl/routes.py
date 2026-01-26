from flask import Blueprint, request, g, jsonify, render_template
from validates.validate_api import validate_route
from validates.validate_db import validate_db_data
import os
from extensions.mongo import mongo
from pymongo.errors import OperationFailure, PyMongoError
from datetime import datetime
import uuid
from db_schemas.logs import logs_schema
from db_schemas.alerts import alerts_schema
from handlers.auth_check_wrapper import auth_check_wrapper
from handlers.send_alert_email import send_alert_email
from log_arbor.utils import log
from domains.service import check_api_blueprint, check_ui_blueprint
from domains.logs.service import write_log, all_user_logs


logs_bl = Blueprint("logs_bl", __name__, template_folder="templates", static_folder="static")

@logs_bl.app_errorhandler(OperationFailure)
def handle_operation_failure(e):

    try:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "critical", f"failed db operation at: {request.path} and error: {str(e)}", "5b522faa-76a4-444c-8253-7f045f5c06af")
    except Exception as loge:

        return {"message": f"{loge}"}, 500
    
    return {"message": "something went wrong"}, 500





@logs_bl.app_errorhandler(PyMongoError)
def handle_operation_failure_pymongo(e):

    try:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "critical", f"failed db operation at: {request.path} and error: {str(e)} because of a pymongo error", "5b522faa-76a4-444c-8253-7f045f5c06af")
    except Exception as loge:

        return {"message": f"{loge}"}, 500
    
    return {"message": "something went wrong"}, 500





@logs_bl.app_errorhandler(Exception)
def handle_operation_failure_exception(e):

    try:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "critical", f"failed at: {request.path} and error: {str(e)}", "5b522faa-76a4-444c-8253-7f045f5c06af")
    except Exception as loge:

        return {"message": f"{loge}"}, 500
    
    return {"message": "something went wrong"}, 500





@logs_bl.before_request
def data_validation():

    if request.method == "POST" and not request.path == "/api/v1/logs/all_logs":

        path = request.path

        data = validate_route(request, path.removeprefix("/api/v1"))

        if "error" in data:

            log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", f"user failed data validation on api_validate on {path}", "5b522faa-76a4-444c-8253-7f045f5c06af")

            return {"message": data}, 400
        
        if not data.get("token") == os.getenv("LOGARBOR_LIBRARY_TOKEN"):

            log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "error", "user tried to access the system not using the library", "5b522faa-76a4-444c-8253-7f045f5c06af")

            return {"message": "invalid library token"}, 401
        
        allowed_log_levels = ["debug", "info", "warning", "error", "critical"]

        if not data.get("level") in allowed_log_levels:

            log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", "invalid log level provided", "5b522faa-76a4-444c-8253-7f045f5c06af")

            return {"message": "invalid log level"}, 401
        
        g.data = data





@logs_bl.route("/", methods=["GET"])
def logs():

    # Checks ui blueprint

    check = check_ui_blueprint(request.blueprint, "logs_bl")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", f"ui route was accessed with non ui blueprint: {request.path}", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"message": check["message"]}, 404
    
    # Renders logs.html

    return render_template("logs.html")





@logs_bl.route("/add", methods=["POST"])
def add_log():

    # Checks api blueprint

    check = check_api_blueprint(request.blueprint, "logs_api")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"message": check["message"]}, 404
    
    # Writes a log

    log_result = write_log(g.data, mongo.db.services, mongo.db.logs, mongo.db.alerts, mongo.db.users, request)

    if not log_result["ok"]:

        return {"message": log_result["message"]}, log_result["status"]
    
    return {"message": log_result["message"]}, 200


    
    

@logs_bl.route("/all_logs", methods=["POST"])
@auth_check_wrapper()
def all_logs():

    # Checks api blueprint

    check = check_api_blueprint(request.blueprint, "logs_api")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"message": check["message"]}, 404

    # Finds all user's logs

    all_logs_result = all_user_logs(mongo.db.services, mongo.db.logs, request)

    return {"message": all_logs_result["message"]}, 200