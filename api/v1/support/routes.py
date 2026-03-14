from flask import Blueprint, request, render_template, g
from pymongo.errors import OperationFailure, PyMongoError
from log_arbor.utils import log
import os
from domains.service import check_api_blueprint, check_ui_blueprint
from handlers.auth_check_wrapper import auth_check_wrapper
from domains.support.service import send_feedback
from validates.validate_api import validate_route
from extensions.limiter import limiter


support_bl = Blueprint("support_bl", __name__, template_folder="templates", static_folder="static")

@support_bl.app_errorhandler(OperationFailure)
def handle_operation_failure(e):

    log(os.getenv("LOGARBOR_SUPPORT_SERVICE_ID"), "critical", f"failed db operation at: {request.path} and error: {e}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))
    
    return {"message": "something went wrong"}, 500





@support_bl.app_errorhandler(PyMongoError)
def handle_operation_failure_pymongo(e):

    log(os.getenv("LOGARBOR_SUPPORT_SERVICE_ID"), "critical", f"failed db operation at: {request.path} and error: {e} because of a pymongo error", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))
    
    return {"message": "something went wrong"}, 500





@support_bl.app_errorhandler(Exception)
def handle_operation_failure_exception(e):
 
    return {"message": "something went wrong"}, 500





@support_bl.before_request
def data_validation():

    if request.method == "POST":

        path = request.path

        data = validate_route(request, path.removeprefix("/api/v1"))

        if "error" in data:

            log(os.getenv("LOGARBOR_SUPPORT_SERVICE_ID"), "warning", f"user failed data validation on api_validate on {path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

            return {"message": data}, 400
        
        g.data = data






@support_bl.route("/", methods=["GET"])
def support():

    # Checks ui blueprint

    check = check_ui_blueprint(request.blueprint, "support_bl")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_SUPPORT_SERVICE_ID"), "warning", f"ui route was accessed with non ui blueprint: {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"message": check["message"]}, 404
    
    # Renders support.html

    return render_template("support.html")





@support_bl.route("/feedback", methods=["GET"])
def feedback():
    
    # Checks ui blueprint

    check = check_ui_blueprint(request.blueprint, "support_bl")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_SUPPORT_SERVICE_ID"), "warning", f"ui route was accessed with non ui blueprint: {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"message": check["message"]}, 404
    
    # Renders feedback.html

    return render_template("feedback.html")





@support_bl.route("/feedback", methods=["POST"])
@limiter.limit("10 per minute")
def post_feedback():
    
    # Checks api blueprint

    check = check_api_blueprint(request.blueprint, "support_api")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_SUPPORT_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"message": check["message"]}, 404
    
    # Sends an email to LogArbor Support Team with feedback

    send_feedback_result = send_feedback(g.data, request)

    if not send_feedback_result["ok"]:

        return {"message": send_feedback_result["message"]}, send_feedback_result["status"]
    
    return {"message": send_feedback_result["message"]}, 200





@support_bl.route("/community", methods=["GET"])
def community_page():
    
    # Checks ui blueprint

    check = check_ui_blueprint(request.blueprint, "support_bl")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_SUPPORT_SERVICE_ID"), "warning", f"ui route was accessed with non ui blueprint: {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"message": check["message"]}, 404
    
    # Renders community.html

    return render_template("community.html")

