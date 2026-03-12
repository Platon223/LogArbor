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
from domains.logs.service import write_log, all_user_logs, get_log_count_metrics, search_logs_by_message, search_logs_by_message_extra, search_logs_by_type, search_logs_by_type_extra, all_user_logs_more
from extensions.limiter import limiter
from tasks.add_log_api_task import add_log_task
from extensions.socket import socketio
from domains.logs.service import get_speed_log_ingection, get_error_rate_metric

logs_bl = Blueprint("logs_bl", __name__, template_folder="templates", static_folder="static")

@logs_bl.app_errorhandler(OperationFailure)
def handle_operation_failure(e):

    try:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "critical", f"failed db operation at: {request.path} and error: {str(e)}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))
    except Exception as loge:

        return {"message": f"{loge}"}, 500
    
    return {"message": "something went wrong"}, 500





@logs_bl.app_errorhandler(PyMongoError)
def handle_operation_failure_pymongo(e):

    try:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "critical", f"failed db operation at: {request.path} and error: {str(e)} because of a pymongo error", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))
    except Exception as loge:

        return {"message": f"{loge}"}, 500
    
    return {"message": "something went wrong"}, 500





@logs_bl.app_errorhandler(Exception)
def handle_operation_failure_exception(e):

    try:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "critical", f"failed at: {request.path} and error: {str(e)}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))
    except Exception as loge:

        return {"message": f"{loge}"}, 500
    
    return {"message": "something went wrong"}, 500





@logs_bl.before_request
def data_validation():

    no_data_validation_endpoints = ["/api/v1/logs/all_logs", "/api/v1/logs/logs_speed_metric", "/api/v1/logs/error_rate_metric"]

    if request.method == "POST" and not request.path in no_data_validation_endpoints:

        path = request.path

        data = validate_route(request, path.removeprefix("/api/v1"))

        if "error" in data:

            log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", f"user failed data validation on api_validate on {path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

            return {"message": data}, 400
        
        if request.path == "/api/v1/logs/add" and not data.get("token") == os.getenv("LOGARBOR_LIBRARY_TOKEN"):

            log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "error", "user tried to access the system not using the library", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

            return {"message": "invalid library token"}, 401
        
        allowed_log_levels = ["debug", "info", "warning", "error", "critical"]

        if request.path == "/api/v1/logs/add" and  not data.get("level") in allowed_log_levels:

            user = mongo.db.users.find_one({"id": data.get("user_id")})

            if not user:

                return {"message": "user not found"}, 404

            result = send_alert_email(
                os.getenv("EMAILJS_SERVICE_ID"), 
                os.getenv("ALERT_SERVICE_TEMPLATE_ID"),
                os.getenv("PUBLIC_EMAILJS_KEY"),
                os.getenv("ACCESS_TOKEN_EMAILJS"),
                user["username"],
                "LogArbor Support Team",
                user["email"],
                "You are receiving this alert because, you provided an invalid log level in the log function call. Please check our docs for log levels. If that doesn't help please contact the LogArbor Support Team."
            )

            log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", "invalid log level provided", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

            return {"message": "invalid log level"}, 401
        
        g.data = data





@logs_bl.route("/", methods=["GET"])
def logs():

    # Checks ui blueprint

    check = check_ui_blueprint(request.blueprint, "logs_bl")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", f"ui route was accessed with non ui blueprint: {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"message": check["message"]}, 404
    
    # Renders logs.html

    return render_template("logs.html")





@logs_bl.route("/add", methods=["POST"])
@limiter.limit("500 per minute")
def add_log():

    # Checks api blueprint

    check = check_api_blueprint(request.blueprint, "logs_api")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"message": check["message"]}, 404
    
    # Writes a log

    add_task_data = {
        "service_id": g.data.get("service_id"),
        "token": g.data.get("token"),
        "message": g.data.get("message"),
        "level": g.data.get("level"),
        "time": g.data.get("time"),
        "user_id": g.data.get("user_id")
    }

    add_log_task.delay(add_task_data)

    socketio.emit("new-log", {"message": "new log"}, room=f"user_{g.data.get('user_id')}")
    
    return {"message": "logged"}, 200


    
    

@logs_bl.route("/all_logs", methods=["POST"])
@auth_check_wrapper()
def all_logs():

    # Checks api blueprint

    check = check_api_blueprint(request.blueprint, "logs_api")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"message": check["message"]}, 404

    # Finds all user's logs

    all_logs_result = all_user_logs(mongo.db.services, mongo.db.logs, request)

    return {"message": all_logs_result["message"]}, 200





@logs_bl.route("/all_logs_extra", methods=["POST"])
@auth_check_wrapper()
def all_logs_extra():

    # Checks api blueprint

    check = check_api_blueprint(request.blueprint, "logs_api")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"message": check["message"]}, 404

    # Loads more user's logs

    all_logs_result = all_user_logs_more(g.data, mongo.db.services, mongo.db.logs, request)

    if not all_logs_result["ok"]:

        return {"message": all_logs_result["message"]}, all_logs_result["status"]

    return {"message": all_logs_result["message"]}, 200





@logs_bl.route("/metrics", methods=["GET"])
@auth_check_wrapper()
def metrics_log_count():

    # Checks api blueprint

    check = check_api_blueprint(request.blueprint, "logs_api")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"message": check["message"]}, 404
    
    # Finds all user's logs

    user_metrics = get_log_count_metrics(mongo.db.services, mongo.db.logs, request)

    return {"message": user_metrics["message"]}, 200





@logs_bl.route("/search_by_message", methods=["POST"])
@auth_check_wrapper()
def search_log():

    # Checks api blueprint

    check = check_api_blueprint(request.blueprint, "logs_api")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"message": check["message"]}, 404
    
    # Filters logs

    filtered_logs = search_logs_by_message(g.data, mongo.db.services, mongo.db.logs, request)

    if not filtered_logs["ok"]:

        return {"message": filtered_logs["message"]}, filtered_logs["status"]
    
    return {"message": filtered_logs["message"]}, 200





@logs_bl.route("/search_by_message_extra", methods=["POST"])
@auth_check_wrapper()
def search_extra_logs():

    # Checks api blueprint

    check = check_api_blueprint(request.blueprint, "logs_api")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"message": check["message"]}, 404
    
    # Searches more logs

    more_filtered_logs = search_logs_by_message_extra(g.data, mongo.db.services, mongo.db.logs, request)

    if not more_filtered_logs["ok"]:

        return {"message": more_filtered_logs["message"]}, more_filtered_logs["status"]
    
    return {"message": more_filtered_logs["message"]}, 200





@logs_bl.route("/search_by_level", methods=["POST"])
@auth_check_wrapper()
def search_log_by_type():

    # Checks api blueprint

    check = check_api_blueprint(request.blueprint, "logs_api")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"message": check["message"]}, 404
    
    # Searches logs by level

    filtered_logs = search_logs_by_type(g.data, mongo.db.services, mongo.db.logs, request)

    if not filtered_logs["ok"]:

        return {"message": filtered_logs["message"]}, filtered_logs["status"]
    
    return {"message": filtered_logs["message"]}, 200





@logs_bl.route("/search_by_level_extra", methods=["POST"])
@auth_check_wrapper()
def search_log_by_type_extra():

    # Checks api blueprint

    check = check_api_blueprint(request.blueprint, "logs_api")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"message": check["message"]}, 404
    
    # Searches more logs by level

    more_filtered_logs = search_logs_by_type_extra(g.data, mongo.db.services, mongo.db.logs, request)

    if not more_filtered_logs["ok"]:

        return {"message": more_filtered_logs["message"]}, more_filtered_logs["status"]
    
    return {"message": more_filtered_logs["message"]}, 200





@logs_bl.route("/logs_speed_metric", methods=["POST"])
@auth_check_wrapper()
def speed_logs_metric():

    # Checks api blueprint

    check = check_api_blueprint(request.blueprint, "logs_api")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"message": check["message"]}, 404
    

    # Gets logs speed

    log_speed_result = get_speed_log_ingection(mongo.db.services, mongo.db.logs, request)

    return {"message": log_speed_result["message"]}, 200





@logs_bl.route("/error_rate_metric", methods=["POST"])
@auth_check_wrapper()
def error_rate_metric():

    
    # Checks api blueprint

    check = check_api_blueprint(request.blueprint, "logs_api")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"message": check["message"]}, 404
    
    # Gets error rate metric

    error_rate_metric_result = get_error_rate_metric(mongo.db.services, mongo.db.logs, request)

    return {"message": error_rate_metric_result["message"]}, 200