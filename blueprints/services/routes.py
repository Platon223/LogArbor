from flask import request, Blueprint, render_template, url_for, redirect, jsonify, g, session
from handlers.auth_check_wrapper import auth_check_wrapper
from validates.validate_api import validate_route
from validates.validate_db import validate_db_data
from db_schemas.services import services_schema
from pymongo.errors import DuplicateKeyError, OperationFailure, PyMongoError
from extensions.mongo import mongo
import uuid
import secrets
import datetime
from datetime import timedelta
import os
from handlers.send_delete_service_email import send_verify_delete_service_email
from db_schemas.verify_codes import verify_codes_schema
from log_arbor.utils import log as loggg
from domains.service import check_api_blueprint, check_ui_blueprint
from domains.services.service import create_service, update_service, request_delete_service


services_bl = Blueprint("services_bl", __name__, template_folder="templates", static_folder="static")

@services_bl.app_errorhandler(OperationFailure)
def handle_operation_failure(e):

    try:

        loggg(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "critical", f"failed db operation at: {request.path} and error: {str(e)}")
    except Exception as loge:

        return {"message": f"{loge}"}, 500
    
    return {"message": "something went wrong"}, 500

@services_bl.app_errorhandler(PyMongoError)
def handle_operation_failure_pymongo(e):

    try:

        loggg(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "critical", f"failed db operation at: {request.path} and error: {str(e)} because of a pymongo error")
    except Exception as loge:

        return {"message": f"{loge}"}, 500
    
    return {"message": "something went wrong"}, 500

@services_bl.app_errorhandler(Exception)
def handle_operation_failure_exception(e):

    try:

        loggg(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "critical", f"failed at: {request.path} and error: {str(e)}")
    except Exception as loge:

        return {"message": f"{loge}"}, 500
    
    return {"message": "something went wrong"}, 500

@services_bl.before_request
def data_validation():

    if request.method == "POST" and not request.path == "/api/v1/services/all_services":

        path = request.path

        data = validate_route(request, path.removeprefix("/api/v1"))

        if "error" in data:
            log("SERVICES", "warning", f"user failed data validation on api_validate on {path}")
            return {"message": data}, 400
        
        g.data = data


@services_bl.route("/", methods=["GET"])
def services():

    # Checks ui blueprint

    check = check_ui_blueprint(request.blueprint, "services_bl")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "warning", f"ui route was accessed with non ui blueprint: {request.path}", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")

        return {"message": check["message"]}, 404
    
    # Renders services.html

    return render_template("services.html")


@services_bl.route("/create", methods=["POST"])
@auth_check_wrapper()
def create():

    # Checks api blueprint

    check = check_api_blueprint(request.blueprint, "services_api")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")

        return {"message": check["message"]}, 404
    
    # Creates a service

    new_service = create_service(g.data, mongo.db.services, request)

    if not new_service["ok"]:

        return {"message": new_service["message"]}, new_service["status"]
    
    return {"message": new_service["message"]}, 200


@services_bl.route("/update_service", methods=["POST"])
@auth_check_wrapper()
def update():

    # Checks api blueprint

    check = check_api_blueprint(request.blueprint, "services_api")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")

        return {"message": check["message"]}, 404
    
    # Updates a service

    updated_service = update_service(g.data, mongo.db.services, request)

    if not updated_service["ok"]:

        return {"message": updated_service["message"]}, updated_service["status"]
    
    return {"message": updated_service["message"]}, 200
    
    

@services_bl.route("/request_delete_service", methods=["POST"])
@auth_check_wrapper()
def request_delete():

    # Checks api blueprint

    check = check_api_blueprint(request.blueprint, "services_api")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")

        return {"message": check["message"]}, 404
    
    # Requests deleting a service

    request_result = request_delete_service(mongo.db.users, mongo.db.verify_codes, request)

    if not request_result["ok"]:

        return {"message": request_result["message"]}, request_result["status"]
    
    return {"message": request_result["message"]}, 200
    
   

@services_bl.route("/confirm_delete_service", methods=["POST"])
@auth_check_wrapper()
def confirm_delete():

    # Checks api blueprint

    check = check_api_blueprint(request.blueprint, "services_api")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")

        return {"message": check["message"]}, 404
    
    

@services_bl.route("/all_services", methods=["POST"])
@auth_check_wrapper()
def all():

    # Checks api blueprint

    check = check_api_blueprint(request.blueprint, "services_api")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")

        return {"message": check["message"]}, 404
    
    all_user_services = mongo.db.services.find({"user_id": getattr(request, "auth_identity", None)})

    all_user_services_list = list(all_user_services)

    if len(all_user_services_list) == 0:
        log("SERVICES", "info", "user has no services yet")
        return {"message": "no services"}, 404

    log("SERVICES", "info", "user got all services successufully")
    return {"message": all_user_services_list}, 200

@services_bl.route("/<service_id>", methods=["GET"])
def service_settings(service_id):

    # Checks ui blueprint

    check = check_ui_blueprint(request.blueprint, "services_bl")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "warning", f"ui route was accessed with non ui blueprint: {request.path}", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")

        return {"message": check["message"]}, 404
    
    # Renders service.html

    return render_template("service.html", serv_id=service_id)

@services_bl.route("/service", methods=["POST"])
@auth_check_wrapper()
def settings_info():

    # Checks api blueprint

    check = check_api_blueprint(request.blueprint, "services_api")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")

        return {"message": check["message"]}, 404
    
    service = mongo.db.services.find_one({"id": g.data.get("service_id"), "user_id": getattr(request, "auth_identity", None)})
    
    if not service:
        log("SERVICES", "warning", "service was not found")
        return {"message": "service not found"}, 404
    
    log("SERVICES", "info", "user has found the service successfully")
    return {
        "message": {
            "id": service["id"],
            "name": service["name"],
            "url": service["url"],
            "alert_level": service["alert_level"]
        }
    }, 200