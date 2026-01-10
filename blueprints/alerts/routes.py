from flask import Blueprint, request, g, jsonify, render_template
from log_arbor.utils import log
from handlers.auth_check_wrapper import auth_check_wrapper
from pymongo.errors import OperationFailure, PyMongoError
import os
from validates.validate_api import validate_route


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
    return render_template("alerts.html")

@alerts_bl.route("/alerts", methods=["GET"])
@auth_check_wrapper()
def all_alerts():
    pass

@alerts_bl.route("/marked_viewed", methods=["POST"])
@auth_check_wrapper()
def mark_as_viewed():
    pass

@alerts_bl.route("/alerts", methods=["DELETE"])
@auth_check_wrapper()
def delete_alert():
    pass
