from flask import request, Blueprint, render_template, url_for, redirect, jsonify, g, session
from handlers.auth_check_wrapper import auth_check_wrapper
from logg.log import log
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


services_bl = Blueprint("services_bl", __name__, template_folder="templates", static_folder="static")

@services_bl.before_request
def data_validation():
    if request.method == "POST" and not request.path == "/services/all_services":
        path = request.path
        data = validate_route(request, path)
        if "error" in data:
            log("AUTH", "warning", f"user failed data validation on api_validate on {path}")
            return {"message": data}, 400
        
        g.data = data


@services_bl.route("/", methods=["GET"])
def services():
    return render_template("services.html")


@services_bl.route("/create", methods=["POST"])
@auth_check_wrapper()
def create():
    try:
        db_data = {
            "id": str(uuid.uuid4()),
            "name": g.data.get("name"),
            "url": g.data.get("url"),
            "alert_level": g.data.get("alert_level"),
            "user_id": getattr(request, "auth_identity", None)
        }

        db_data_validated = validate_db_data(db_data, services_schema)
        if "error" in db_data_validated:
            log("AUTH", "warning", "user failed data validation on db_validate on /services/create")
            return {"message": db_data_validated}, 400
        
        mongo.db.services.insert_one(db_data)
    except OperationFailure as e:
        log("SERVICES", "critical", f"failed creating a new service at /services/create: {e}")
        return {"message": "something went wrong"}, 500
    except PyMongoError as e:
        log("SERVICES", "critical", f"failed creating a new service at /services/create: {e}, pymongo error")
        return {"message": "something went wrong"}, 500
    except Exception as e:
        log("SERVICES", "critical", f"something went wrong at /services/create: {e}")
        return {"message": "something went wrong"}, 500
    
    log("SERVICES", "info", "user created a services successfully")
    return {"message": "created"}, 200


@services_bl.route("/update_service", methods=["POST"])
@auth_check_wrapper()
def update():
    try:
        if g.data.get("parameter") == "name" or "url" or "alert_level":
            filter_query = {"id": g.data.get("service_id"), "user_id": getattr(request, "auth_identity", None)}

            update_operation = {
                "$set": {
                    f"{g.data.get('parameter')}": g.data.get("value")
                }
            }

            mongo.db.services.update_one(filter_query, update_operation)
        else:
            log("SERVICES", "critical", "unknown parameter was provided at /services/update_service")
            return {"message": "unknown parameter"}
    except OperationFailure as e:
        log("SERVICES", "critical", f"failed updating a service at /services/update_service: {e}")
        return {"message": "something went wrong"}, 500
    except PyMongoError as e:
        log("SERVICES", "critical", f"failed updating a service at /services/update_service: {e}, pymongo error")
        return {"message": "something went wrong"}, 500
    except Exception as e:
        log("SERVICES", "critical", f"something went wrong at /services/update_service: {e}")
        return {"message": "something went wrong"}, 500
    
    log("SERVICES", "info", f"user updated service: {g.data.get('service_id')} successufully")
    return {"message": "updated"}, 200

@services_bl.route("/request_delete_service", methods=["POST"])
@auth_check_wrapper()
def request_delete():
    try:
        user = mongo.db.users.find_one({"id": getattr(request, "auth_identity", None)})

        verification_code = str(secrets.randbelow(1000000)).zfill(6)

        result = send_verify_delete_service_email(
            os.getenv("EMAILJS_SERVICE_ID"), 
            os.getenv("DELETE_SERVICE_TEMPLATE_ID"),
            os.getenv("PUBLIC_EMAILJS_KEY"),
            os.getenv("ACCESS_TOKEN_EMAILJS"),
            "LogArbor Support Team",
            user["email"],
            verification_code
        )

        if not result == "success":
            log("AUTH", "critical", f"User: {user['username']} failed to receive verification code email")
            return {"message": f"something went wrong while sending an email: {result}"}



        db_verify_code_data = {
            "id": str(uuid.uuid4()),
            "code": verification_code,
            "user_id": user["id"],
            "expiration_date": datetime.datetime.today() + timedelta(minutes=5)
        }
        db_verify_code_data_validate = validate_db_data(db_verify_code_data, verify_codes_schema)
        if "error" in db_verify_code_data_validate:
            log("AUTH", "warning", "user failed data validation on db_validate on login during verify code inserting")
            return {"message": db_verify_code_data_validate}, 400
            
        mongo.db.verify_codes.insert_one(db_verify_code_data)
    except OperationFailure as e:
        log("SERVICES", "critical", f"failed requesting to delete a service at /services/request_delete_service: {e}")
        return {"message": "something went wrong"}, 500
    except PyMongoError as e:
        log("SERVICES", "critical", f"failed requesting to delete a service at /services/request_delete_service: {e}, pymongo error")
        return {"message": "something went wrong"}, 500
    except Exception as e:
        log("SERVICES", "critical", f"something went wrong at /services/request_delete_service: {e}")
        return {"message": "something went wrong"}, 500
    
    log("SERVICES", "info", f"user requested to delete a service: {g.data.get('service_id')} successufully")
    session["service_id"] = g.data.get('service_id')
    return {"message": "sent"}, 200

@services_bl.route("/all_services", methods=["POST"])
@auth_check_wrapper()
def all():
    try:
        all_user_services = mongo.db.services.find({"user_id": getattr(request, "auth_identity", None)})
    except OperationFailure as e:
        log("SERVICES", "critical", f"failed getting all services at /services/all_services: {e}")
        return {"message": "something went wrong"}, 500
    except PyMongoError as e:
        log("SERVICES", "critical", f"failed getting all services at /services/all_services: {e}, pymongo error")
        return {"message": "something went wrong"}, 500
    except Exception as e:
        log("SERVICES", "critical", f"something went wrong at /services/all_services: {e}")
        return {"message": "something went wrong"}, 500
    


    all_user_services_list = list(all_user_services)

    if len(all_user_services_list) == 0:
        log("SERVICES", "info", "user has no services yet")
        return {"message": "no services"}, 404

    log("SERVICES", "info", "user got all services successufully")
    return {"message": all_user_services_list}, 200

@services_bl.route("/<service_id>", methods=["GET"])
def service_settings(service_id):
    return render_template("service.html", serv_id=service_id)

@services_bl.route("/service", methods=["POST"])
@auth_check_wrapper()
def settings_info():
    try:
        service = mongo.db.services.find_one({"id": g.data.get("service_id"), "user_id": getattr(request, "auth_identity", None)})
    except OperationFailure as e:
        log("SERVICES", "critical", f"failed getting a service at /services/service: {e}")
        return {"message": "something went wrong"}, 500
    except PyMongoError as e:
        log("SERVICES", "critical", f"failed getting a service at /services/service: {e}, pymongo error")
        return {"message": "something went wrong"}, 500
    except Exception as e:
        log("SERVICES", "critical", f"something went wrong at /services/service: {e}")
        return {"message": "something went wrong"}, 500
    
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