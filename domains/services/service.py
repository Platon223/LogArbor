from log_arbor.utils import log
import os
import uuid
from validates.validate_db import validate_db_data
from db_schemas.services import services_schema
from db_schemas.verify_codes import verify_codes_schema
import secrets
import datetime
from datetime import timedelta
from handlers.send_delete_service_email import send_verify_delete_service_email


def create_service(global_data, services_collection, request):
    
    '''
        Creates a new service
    '''

    db_data = {
        "id": str(uuid.uuid4()),
        "name": global_data.get("name"),
        "url": global_data.get("url"),
        "alert_level": global_data.get("alert_level"),
        "user_id": getattr(request, "auth_identity", None)
    }

    db_data_validated = validate_db_data(db_data, services_schema)
    if "error" in db_data_validated:

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "warning", f"user failed data validation on db_validate on {request.path}", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"ok": False, "message": db_data_validated, "status": 400}
        
    services_collection.insert_one(db_data)
    
    
    log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "info", "user created a services successfully", "5b522faa-76a4-444c-8253-7f045f5c06af")

    return {"ok": True, "message": "created"}





def update_service(global_data, services_collection, request):

    '''
        Updates a service
    '''

    if global_data.get("parameter") == "name" or "url" or "alert_level":

        filter_query = {"id": global_data.get("service_id"), "user_id": getattr(request, "auth_identity", None)}

        update_operation = {
            "$set": {
                f"{global_data.get('parameter')}": global_data.get("value")
            }
        }

        services_collection.update_one(filter_query, update_operation)
    else:

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "critical", f"unknown parameter was provided at {request.path}", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"ok": False, "message": "unknown parameter", "status": 404}
    
    
    log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "info", "user updated successufully", "5b522faa-76a4-444c-8253-7f045f5c06af")

    return {"ok": True, "message": "updated"}





def request_delete_service(users_collection, verify_codes_collection, request):

    '''
        Sends a request to delete a service
    '''

    user = users_collection.find_one({"id": getattr(request, "auth_identity", None)})

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

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "critical", "User failed to receive verification code email", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"ok": False, "message": f"something went wrong while sending an email: {result}", "status": 500}



    db_verify_code_data = {
        "id": str(uuid.uuid4()),
        "code": verification_code,
        "user_id": user["id"],
        "expiration_date": datetime.datetime.today() + timedelta(minutes=5)
    }
    
    db_verify_code_data_validate = validate_db_data(db_verify_code_data, verify_codes_schema)
    if "error" in db_verify_code_data_validate:

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "warning", "user failed data validation on db_validate on login during verify code inserting", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"ok": False, "message": db_verify_code_data_validate, "status": 400}
            
    verify_codes_collection.insert_one(db_verify_code_data)
    
    
    log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "info", "user requested to delete a service successufully", "5b522faa-76a4-444c-8253-7f045f5c06af")

    return {"ok": True, "message": "sent"}





def confirm_delete_service(global_data, verify_codes_collection, services_collection, request):

    '''
        Confirms deletion of a service
    '''

    current_verify_code = verify_codes_collection.find_one({"code": global_data.get("code"), "user_id": getattr(request, "auth_identity", None)})

    if not current_verify_code:

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "warning", "user has provided a wrong verification code at delete service confirmation", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"ok": False, "message": "invalid code", "status": 401}
        
    if current_verify_code["expiration_date"] < datetime.datetime.today():

        verify_codes_collection.delete_one({"id": current_verify_code["id"]})

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "info", "user's verification code has been expired at delete service confirmation", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"ok": False, "message": "expired", "status": 401}
        
    verify_codes_collection.delete_one({"id": current_verify_code["id"]})

    services_collection.delete_one({"id": global_data.get("service_id")})
    
    
    log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "info", "user deleted their service successfully", "5b522faa-76a4-444c-8253-7f045f5c06af")

    return {"ok": True, "message": "deleted"}





def all_services(services_collection, request):

    '''
        Finds all services user have created
    '''

    all_user_services = services_collection.find({"user_id": getattr(request, "auth_identity", None)})

    all_user_services_list = list(all_user_services)

    if len(all_user_services_list) == 0:

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "info", "user has no services yet", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"ok": True, "message": "no services"}

    log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "info", "user got all services successufully", "5b522faa-76a4-444c-8253-7f045f5c06af")

    return {"ok": True, "message": all_user_services_list}





def service(global_data, services_collection, request):

    '''
        Finds settings about a speciffic service
    '''

    service = services_collection.find_one({"id": global_data.get("service_id"), "user_id": getattr(request, "auth_identity", None)})
    
    if not service:

        log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "warning", "service was not found", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"ok": False, "message": "service not found", "status": 404}
    
    log(os.getenv("LOGARBOR_SERVICES_SERVICE_ID"), "info", "user has found the service successfully", "5b522faa-76a4-444c-8253-7f045f5c06af")

    return {
        "ok": True,
        "message": {
            "id": service["id"],
            "name": service["name"],
            "url": service["url"],
            "alert_level": service["alert_level"]
        }
    }