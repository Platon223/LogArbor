from flask import Blueprint, request, g, jsonify, render_template
from validates.validate_api import validate_route
from validates.validate_db import validate_db_data
from logg.log import log
import os
from extensions.mongo import mongo
from pymongo.errors import OperationFailure, PyMongoError
from datetime import datetime
import uuid
from db_schemas.logs import logs_schema
from db_schemas.alerts import alerts_schema
from handlers.auth_check_wrapper import auth_check_wrapper
from dotenv import load_dotenv
from handlers.send_alert_email import send_alert_email
from log_arbor.utils import log as loggg

load_dotenv(dotenv_path='../../.env')

logs_bl = Blueprint("logs_bl", __name__, template_folder="templates", static_folder="static")

@logs_bl.app_errorhandler(OperationFailure)
def handle_operation_failure(e):
    
    
    return {"message": f"sm tnew wr: {e}"}, 500

@logs_bl.app_errorhandler(PyMongoError)
def handle_operation_failure_pymongo(e):
    
    
    return {"message": f"sm tnew wr: {e}"}, 500

@logs_bl.app_errorhandler(Exception)
def handle_operation_failure_exception(e):
    
    return {"message": f"sm tnew wr: {e}"}, 500

@logs_bl.before_request
def data_validation():
    if request.method == "POST" and not request.path == "/api/v1/logs/all_logs":
        path = request.path
        data = validate_route(request, path - "/api/v1")
        if "error" in data:
            log("AUTH", "warning", f"user failed data validation on api_validate on {path}")
            return {"message": data}, 400
        
        if not data.get("token") == os.getenv("LOGARBOR_LIBRARY_TOKEN"):
            log("LOGS", "error", "user tried to access the system not using the library")
            return {"message": "invalid library token"}, 401
        
        allowed_log_levels = ["debug", "info", "warning", "error", "critical"]
        if not data.get("level") in allowed_log_levels:
            log("LOGS", "warning", "invalid log level provided")
            return {"message": "invalid log level"}, 401
        
        g.data = data

@logs_bl.route("/", methods=["GET"])
def logs():
    if not request.blueprint == "logs_bl":
        loggg(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", f"ui route: /, was accessed with non ui blueprint: {request.path}")
        return {"message": "ui route only"}, 404

    return render_template("logs.html")

@logs_bl.route("/add", methods=["POST"])
def add_log():

    if not request.blueprint == "logs_api":
        loggg(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", f"api route: /add, was accessed with non api blueprint: {request.path}")
        return {"message": "api route only"}, 404
    
    service = mongo.db.services.find_one({"id": g.data.get("service_id")})
    
    if not service:
        log("LOGS", "error", "service couldn't be found on /logs/add")
        return {"message": "service not found"}, 404
    

    new_log_db_data = {
        "id": str(uuid.uuid4()),
        "service_id": service["id"],
        "message": g.data.get("message"),
        "level": g.data.get("level"),
        "time": g.data.get("time")
    }

    db_validated_data = validate_db_data(new_log_db_data, logs_schema)
    if "error" in db_validated_data:
        log("LOGS", "warning", "user failed data validation on db_validate on /logs/add")
        return {"message": db_validated_data}, 400
    

    mongo.db.logs.insert_one(new_log_db_data)

    
    level_of_logs = ["debug", "info", "warning", "error", "critical"]
    
    if level_of_logs.index(g.data.get("level")) >= level_of_logs.index(service["alert_level"]):
        
        alert_db_data = {
            "id": str(uuid.uuid4()),
            "message": g.data.get("message"),
            "level": g.data.get("level"),
            "time": g.data.get("time")
        }
        alert_db_data_validated = validate_db_data(alert_db_data, alerts_schema)
        if "error" in alert_db_data_validated:
            log("LOGS", "critical", "user failed data validation on db_validate on /logs/add")
            return {"message": "something went wrong"}, 400
        
        
        mongo.db.alerts.insert_one(alert_db_data)

        current_user = mongo.db.users.find_one({"id": service["user_id"]})

        if not current_user:
            loggg(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", "user not found at alert sending api")
            return {"message": "user not found"}, 404
        
        alert_message = f"You are receving this email because LogArbor Alert System has detected a log that had the same or worse than your service's({service["name"]} alert level)"
        
        result = send_alert_email(
            os.getenv("EMAILJS_SERVICE_ID"), 
            os.getenv("ALERT_SERVICE_TEMPLATE_ID"),
            os.getenv("PUBLIC_EMAILJS_KEY"),
            os.getenv("ACCESS_TOKEN_EMAILJS"),
            current_user["username"],
            "LogArbor Support Team",
            current_user["email"],
            alert_message
        )

        if not result == "success":
            log("AUTH", "critical", f"User: {current_user['username']} failed to receive an alert email")
            return {"message": f"something went wrong while sending an alert email: {result}"}
        
    return {"message": "logged"}, 202

@logs_bl.route("/all_logs", methods=["POST"])
@auth_check_wrapper()
def all_logs():

    if not request.blueprint == "logs_api":
        loggg(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", f"api route: /all_logs, was accessed with non api blueprint: {request.path}")
        return {"message": "api route only"}, 404

    services = mongo.db.services.find({"user_id": getattr(request, "auth_identity", None)})
    

    services_list = list(services)

    if len(services_list) == 0:
        log("LOGS", "info", "user has no services yet")
        return {"message": "no services"}, 200

    logs_list = []


    for service in services_list:
        service_logs = mongo.db.logs.find({"service_id": service["id"]})
        service_logs_list = list(service_logs)
        service_obj = {
            "service_id": service["id"],
            "service_name": service["name"], 
            "logs": service_logs_list
        }

        logs_list.append(service_obj)
    

    return {"message": logs_list}, 200