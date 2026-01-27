from flask import Blueprint, request, g, jsonify, render_template
from log_arbor.utils import log
from handlers.auth_check_wrapper import auth_check_wrapper
from pymongo.errors import OperationFailure, PyMongoError
import os
from validates.validate_api import validate_route
from dotenv import load_dotenv
from extensions.mongo import mongo

load_dotenv(dotenv_path='../../.env')


alerts_bl = Blueprint("alerts_bl", __name__, template_folder="templates", static_folder="static")

@alerts_bl.app_errorhandler(OperationFailure)
def handle_operation_failure(e):
    try:
        log(os.getenv("LOGARBOR_ALERT_SERVICE_ID"), "critical", f"failed db operation at: {request.path} and error: {str(e)}")
    except Exception as loge:
        return {"message": f"{loge}"}, 500
    return {"message": "something went wrong"}, 500

@alerts_bl.app_errorhandler(PyMongoError)
def handle_operation_failure_pymongo(e):
    try:
        log(os.getenv("LOGARBOR_ALERT_SERVICE_ID"), "critical", f"failed db operation at: {request.path} and error: {str(e)} because of a pymongo error")
    except Exception as loge:
        return {"message": f"{loge}"}, 500
    return {"message": "something went wrong"}, 500

@alerts_bl.app_errorhandler(Exception)
def handle_operation_failure_exception(e):
    try:
        log(os.getenv("LOGARBOR_ALERT_SERVICE_ID"), "critical", f"failed at: {request.path} and error: {str(e)}")
    except Exception as loge:
        return {"message": f"{loge}"}, 500
    return {"message": "something went wrong"}, 500

@alerts_bl.before_request
def data_validation():
    allowed_http_methods = ["POST", "DELETE"]

    if request.method in allowed_http_methods:
        path = request.path
        data = validate_route(request, path.removeprefix("/api/v1"))
        if "error" in data:
            log("AUTH", "warning", f"user failed data validation on api_validate on {path}")
            return {"message": data}, 400
        
        g.data = data

@alerts_bl.route("/", methods=["GET"])
def alerts():
    if not request.blueprint == "alerts_bl":
        log(os.getenv("LOGARBOR_ALERTS_SERVICE_ID"), "warning", f"ui route: /, was accessed with non ui blueprint: {request.path}")
        return {"message": "ui route only"}, 404

    return render_template("alerts.html")

@alerts_bl.route("/alerts", methods=["GET"])
@auth_check_wrapper()
def all_alerts():
    if not request.blueprint == "alerts_api":
        log(os.getenv("LOGARBOR_ALERTS_SERVICE_ID"), "warning", f"api route: /alerts, was accessed with non api blueprint: {request.path}")
        return {"message": "api route only"}, 404

    current_alerts = mongo.db.alerts.find({"user_id": getattr(request, "auth_identity", None)})

    current_alerts_list = list(current_alerts)

    if len(current_alerts_list) == 0:
        return {"message": "no alerts"}, 200
    
    return {"message": current_alerts_list}, 200

@alerts_bl.route("/marked_viewed", methods=["POST"])
@auth_check_wrapper()
def mark_as_viewed():
    if not request.blueprint == "alerts_api":
        log(os.getenv("LOGARBOR_ALERTS_SERVICE_ID"), "warning", f"api route: /marked_viewed, was accessed with non api blueprint: {request.path}")
        return {"message": "api route only"}, 404

    alert = mongo.db.alerts.find_one({"id": g.data.get("alert_id"), "user_id": getattr(request, "auth_identity", None)})

    if not alert:
        return {"message": "alert not found"}, 404
    
    filter_query = {"id": g.data.get("alert_id"), "user_id": getattr(request, "auth_identity", None)}

    update_operation = {
        "$set": {
            "viewed": g.data.get("status")
        }
    }

    mongo.db.alerts.update_one(filter_query, update_operation)

    return {"message": "marked as viewed"}, 200

@alerts_bl.route("/alerts", methods=["DELETE"])
@auth_check_wrapper()
def delete_alert():
    if not request.blueprint == "alerts_api":
        log(os.getenv("LOGARBOR_ALERTS_SERVICE_ID"), "warning", f"api route: /alerts (DELETE), was accessed with non api blueprint: {request.path}")
        return {"message": "api route only"}, 404

    alert = mongo.db.alerts.find_one({"id": g.data.get("alert_id"), "user_id": getattr(request, "auth_identity", None)})

    if not alert:
        return {"message": "alert not found"}, 404
    
    mongo.db.alerts.delete_one({"id": g.data.get("alert_id"), "user_id": getattr(request, "auth_identity", None)})

    return {"message": "deleted"}, 200
