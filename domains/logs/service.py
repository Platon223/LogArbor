from log_arbor.utils import log
import os
import uuid
from validates.validate_db import validate_db_data
from db_schemas.logs import logs_schema
from db_schemas.alerts import alerts_schema
from handlers.send_alert_email import send_alert_email
from logg.log import log as logg


def write_log(global_data, services_collection, logs_collection, alerts_collection, users_collection, request):

    '''
        Writes a log to a service
    '''

    service = services_collection.find_one({"id": global_data.get("service_id")})
    
    if not service:

        return {"ok": False, "message": "service not found", "status": 404}
    
    if not service["user_id"] == global_data.get("user_id"):

        return {"ok": False, "message": "invalid access token provided", "status": 401}
    

    new_log_db_data = {
        "id": str(uuid.uuid4()),
        "service_id": service["id"],
        "message": global_data.get("message"),
        "level": global_data.get("level"),
        "time": global_data.get("time")
    }

    db_validated_data = validate_db_data(new_log_db_data, logs_schema)

    if "error" in db_validated_data:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", f"user failed data validation on db_validate on {request.path}", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"ok": False, "message": db_validated_data, "status": 401}
    

    logs_collection.insert_one(new_log_db_data)

    
    level_of_logs = ["debug", "info", "warning", "error", "critical"]
    
    if level_of_logs.index(global_data.get("level")) >= level_of_logs.index(service["alert_level"]):
        
        alert_db_data = {
            "id": str(uuid.uuid4()),
            "message": global_data.get("message"),
            "level": global_data.get("level"),
            "time": global_data.get("time"),
            "user_id": global_data.get("user_id"),
            "service_id": service["id"],
            "service_name": service["name"],
            "viewed": False
        }

        alert_db_data_validated = validate_db_data(alert_db_data, alerts_schema)

        if "error" in alert_db_data_validated:

            log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "critical", f"user failed data validation on db_validate on {request.path}", "5b522faa-76a4-444c-8253-7f045f5c06af")

            return {"ok": False, "message": alert_db_data_validated, "status": 401}
        
        
        alerts_collection.insert_one(alert_db_data)

        current_user = users_collection.find_one({"id": service["user_id"]})

        if not current_user:

            log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", "user not found at alert sending api", "5b522faa-76a4-444c-8253-7f045f5c06af")

            return {"ok": False, "message": "user not found", "status": 404}
        
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

            log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "critical", f"User: {current_user['username']} failed to receive an alert email", "5b522faa-76a4-444c-8253-7f045f5c06af")

            return {"ok": False, "message": f"something went wrong while sending an alert email: {result}", "status": 500}
        
    return {"ok": True, "message": "logged"}




def all_user_logs(services_collection, logs_collection, request):

    '''
        Returns all user's logs
    '''

    services = services_collection.find({"user_id": getattr(request, "auth_identity", None)})

    services_list = list(services)

    if len(services_list) == 0:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "info", "user has no services yet", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"ok": True, "message": "no services"}

    logs_list = []

    for service in services_list:

        service_logs = logs_collection.find({"service_id": service["id"]})

        service_logs_list = list(service_logs)

        service_obj = {
            "service_id": service["id"],
            "service_name": service["name"], 
            "logs": service_logs_list
        }

        logs_list.append(service_obj)
    
    return {"ok": True, "message": logs_list}