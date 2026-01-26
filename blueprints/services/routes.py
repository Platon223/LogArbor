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
from log_arbor.utils import log
from domains.service import check_api_blueprint, check_ui_blueprint
from domains.services.service import create_service, update_service, request_delete_service, confirm_delete_service, all_services, service


services_bl = Blueprint("services_bl", __name__, template_folder="templates", static_folder="static")

@services_bl.app_errorhandler(OperationFailure)
def handle_operation_failure(e):

    try:

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "critical", f"failed db operation at: {request.path} and error: {str(e)}", "5b522faa-76a4-444c-8253-7f045f5c06af")
    except Exception as loge:

        return {"message": f"{loge}"}, 500
    
    return {"message": "something went wrong"}, 500





@services_bl.app_errorhandler(PyMongoError)
def handle_operation_failure_pymongo(e):

    try:

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "critical", f"failed db operation at: {request.path} and error: {str(e)} because of a pymongo error", "5b522faa-76a4-444c-8253-7f045f5c06af")
    except Exception as loge:

        return {"message": f"{loge}"}, 500
    
    return {"message": "something went wrong"}, 500






@services_bl.app_errorhandler(Exception)
def handle_operation_failure_exception(e):

    try:

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "critical", f"failed at: {request.path} and error: {str(e)}", "5b522faa-76a4-444c-8253-7f045f5c06af")
    except Exception as loge:

        return {"message": f"{loge}"}, 500
    
    return {"message": "something went wrong"}, 500





@services_bl.before_request
def data_validation():

    if request.method == "POST" and not request.path == "/api/v1/services/all_services":

        path = request.path

        data = validate_route(request, path.removeprefix("/api/v1"))

        if "error" in data:
            log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "warning", f"user failed data validation on api_validate on {path}", "5b522faa-76a4-444c-8253-7f045f5c06af")
            return {"message": data}, 400
        
        g.data = data






@services_bl.route("/", methods=["GET"])
def services():

    # Checks ui blueprint

    check = check_ui_blueprint(request.blueprint, "services_bl")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "warning", f"ui route was accessed with non ui blueprint: {request.path}", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"message": check["message"]}, 404
    
    # Renders services.html

    return render_template("services.html")





@services_bl.route("/create", methods=["POST"])
@auth_check_wrapper()
def create():

    # Checks api blueprint

    check = check_api_blueprint(request.blueprint, "services_api")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", "5b522faa-76a4-444c-8253-7f045f5c06af")

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

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", "5b522faa-76a4-444c-8253-7f045f5c06af")

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

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", "5b522faa-76a4-444c-8253-7f045f5c06af")

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

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"message": check["message"]}, 404
    
    # Deletes a service
    
    confirm_result = confirm_delete_service(g.data, mongo.db.verify_codes, mongo.db.services, request)

    if not confirm_result["ok"]:

        return {"message": confirm_result["message"]}, confirm_result["status"]
    
    return {"message": confirm_result["message"]}, 200





@services_bl.route("/all_services", methods=["POST"])
@auth_check_wrapper()
def all():

    # Checks api blueprint

    check = check_api_blueprint(request.blueprint, "services_api")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"message": check["message"]}, 404
    
    # Finds all services

    all_services_result = all_services(mongo.db.services, request)

    return {"message": all_services_result["message"]}, 200





@services_bl.route("/<service_id>", methods=["GET"])
def service_settings(service_id):

    # Checks ui blueprint

    check = check_ui_blueprint(request.blueprint, "services_bl")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "warning", f"ui route was accessed with non ui blueprint: {request.path}", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"message": check["message"]}, 404
    
    # Renders service.html

    return render_template("service.html", serv_id=service_id)





@services_bl.route("/service", methods=["POST"])
@auth_check_wrapper()
def settings_info():

    # Checks api blueprint

    check = check_api_blueprint(request.blueprint, "services_api")

    if not check["ok"]:

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "warning", f"api route was accessed with non api blueprint: {request.path}", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"message": check["message"]}, 404
    
    # Gets service settings

    service_result = service(g.data, mongo.db.services, request)

    if not service_result["ok"]:

        return {"message": service_result["message"]}, service_result["status"]
    
    return {"message": service_result["message"]}, 200