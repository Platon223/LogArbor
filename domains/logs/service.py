from log_arbor.utils import log
import os
import uuid
from validates.validate_db import validate_db_data
from db_schemas.logs import logs_schema
from db_schemas.alerts import alerts_schema
from handlers.send_alert_email import send_alert_email
import datetime
from datetime import timedelta
from extensions.socket import socketio
from datetime import timezone

def write_log(global_data, services_collection, logs_collection, alerts_collection, users_collection):

    '''
        Writes a log to a service
    '''

    user = users_collection.find_one({"id": global_data.get("user_id")})

    if not user:

        return {"ok": False, "message": "user not found", "status": 404}

    service = services_collection.find_one({"id": global_data.get("service_id")})

    if not service:
 
        result = send_alert_email(
            os.getenv("EMAILJS_SERVICE_ID"), 
            os.getenv("ALERT_SERVICE_TEMPLATE_ID"),
            os.getenv("PUBLIC_EMAILJS_KEY"),
            os.getenv("ACCESS_TOKEN_EMAILJS"),
            user["username"],
            "LogArbor Support Team",
            user["email"],
            "You are receiving this alert because, service was not found on log function call"
        )

        return {"ok": False, "message": "service not found", "status": 404}


 
    if not service["user_id"] == global_data.get("user_id"):

        result = send_alert_email(
            os.getenv("EMAILJS_SERVICE_ID"), 
            os.getenv("ALERT_SERVICE_TEMPLATE_ID"),
            os.getenv("PUBLIC_EMAILJS_KEY"),
            os.getenv("ACCESS_TOKEN_EMAILJS"),
            user["username"],
            "LogArbor Support Team",
            user["email"],
            "You are receiving this alert because, access token provided in you log() function doesn't match the service you are trying to reach"
        )

        return {"ok": False, "message": "invalid access token provided", "status": 401}
    
    if service["log_retention"] < datetime.datetime.today():

        logs_collection.delete_many({"user_id": global_data.get("user_id"), "service_id": service["id"]})

        filter_query = {"id": global_data.get("service_id"), "user_id": global_data.get("user_id")}

        update_operation = {
            "$set": {
                "log_retention": datetime.datetime.today() + timedelta(minutes=10) # For development purposes
            }
        }

        services_collection.update_one(filter_query, update_operation)
    
    services_logs = logs_collection.find({"service_id": global_data.get("service_id")})

    services_logs_list = list(services_logs)

    if len(services_logs_list) >= 600:

        result = send_alert_email(
            os.getenv("EMAILJS_SERVICE_ID"), 
            os.getenv("ALERT_SERVICE_TEMPLATE_ID"),
            os.getenv("PUBLIC_EMAILJS_KEY"),
            os.getenv("ACCESS_TOKEN_EMAILJS"),
            user["username"],
            "LogArbor Support Team",
            user["email"],
            f"Service: {service['name']} log count exceeded. Consider creating a new service. In the next version of LogArbor we will have different packages you can purchase for a speciffic log volume."
        )

        return {"ok": False, "message": "log count for a service exceeded", "status": 401}
    
    new_log_db_data = {
        "id": str(uuid.uuid4()),
        "service_id": service["id"],
        "user_id": global_data.get("user_id"),
        "message": global_data.get("message"),
        "level": global_data.get("level"),
        "time": global_data.get("time")
    }

    db_validated_data = validate_db_data(new_log_db_data, logs_schema)

    if "error" in db_validated_data:

        return {"ok": False, "message": db_validated_data, "status": 401}
    
    logs_collection.insert_one(db_validated_data)


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

            return {"ok": False, "message": alert_db_data_validated, "status": 401}
        
        
        alerts_collection.insert_one(alert_db_data)

        current_user = users_collection.find_one({"id": service["user_id"]})

        if not current_user:

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

            return {"ok": False, "message": f"something went wrong while sending an alert email: {result}", "status": 500}
        
    return {"ok": True, "message": "logged"}




def all_user_logs(services_collection, logs_collection, request):

    '''
        Returns all user's logs
    '''

    services = services_collection.find({"user_id": getattr(request, "auth_identity", None)})

    services_list = list(services)

    if len(services_list) == 0:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "info", "user has no services yet", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": True, "message": "no services"}

    logs_list = []

    for service in services_list:

        service_logs = logs_collection.find({"service_id": service["id"]})

        service_logs_list = list(service_logs)

        if len(service_logs_list) > 50:
            service_logs_list = service_logs_list[:50]

        service_obj = {
            "service_id": service["id"],
            "service_name": service["name"], 
            "logs": service_logs_list
        }

        logs_list.append(service_obj)
    
    
    return {"ok": True, "message": logs_list}





def all_user_logs_more(global_data, services_collection, logs_collection, request):

    '''
        Loads more logs
    '''

    service = services_collection.find_one({"user_id": getattr(request, "auth_identity", None), "id": global_data.get("service_id")})

    if not service:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", "service was not found", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": False, "message": "service was not found", "status": 404}
    
    more_logs = logs_collection.find({"service_id": service["id"]})

    more_logs_list = list(more_logs)

    if len(more_logs_list) > global_data.get("extra"):
        more_logs_list = more_logs_list[:global_data.get("extra")]
    
    return {"ok": True, "message": more_logs_list}




def get_log_count_metrics(services_collection, logs_collection, request):

    '''
        Gets user's amount of logs each day for every service
    '''

    all_user_services = services_collection.find({"user_id": getattr(request, "auth_identity", None)})

    all_user_services_list = list(all_user_services)

    if len(all_user_services_list) == 0:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "info", "user has no services yet", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": True, "message": "no services"}
    
    metrics_list = []
    
    for service in all_user_services_list:

        filtered_logs_list = []

        user_logs = logs_collection.find({"service_id": service["id"]})

        user_logs_list = list(user_logs)

        user_logs_list.append({"time": "arrayendingforlogic"})

        date = ""
        count = 0

        for logg in user_logs_list:

            log_time_string = logg["time"]

            if log_time_string[0:10] == date:
                
                count += 1
            else:

                filtered_log_object = {
                    "date": date,
                    "count": count
                }

                filtered_logs_list.append(filtered_log_object)
                
                date = log_time_string[0:10]

                count = 1
        
        metric_object = {
            "service_name": service["name"],
            "service_id": service["id"],
            "logs_metrics": filtered_logs_list
        }

        metrics_list.append(metric_object)

    return {"ok": True, "message": metrics_list}





def search_logs_by_message(global_data, services_collection, logs_collection, request):

    '''
        Searches logs by message in a service
    '''

    service = services_collection.find_one({"id": global_data.get("service_id"), "user_id": getattr(request, "auth_identity", None)})

    if not service:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", "service was not found", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": False, "message": "service not found", "status": 404}
    
    logs = logs_collection.find({"service_id": service["id"], "message": { "$regex": global_data.get("message"), "$options": "i"}})

    logs_list = list(logs)

    if len(logs_list) == 0:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "info", "no logs were found", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": True, "message": "no logs found"}
    
    if len(logs_list) > 50:

        filtered_logs = logs_list[:50]

        return {"ok": True, "message": filtered_logs}
    else:

        return {"ok": True, "message": logs_list}
    




def search_logs_by_message_extra(global_data, services_collection, logs_collection, request):

    '''
        Searches for more logs in a service
    '''

    service = services_collection.find_one({"id": global_data.get("service_id"), "user_id": getattr(request, "auth_identity", None)})

    if not service:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", "service was not found", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": False, "message": "service not found", "status": 404}
    
    logs = logs_collection.find({"service_id": service["id"], "message": global_data.get("message")})

    logs_list = list(logs)

    if len(logs_list) == 0:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "info", "no logs were found", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": True, "message": "no logs found"}
    
    if len(logs_list) > global_data.get("extra"):

        filtered_logs = logs_list[:global_data.get("extra")]

        return {"ok": True, "message": filtered_logs}
    else:

        return {"ok": True, "message": logs_list}





def search_logs_by_type(global_data, services_collection, logs_collection, request):

    '''
        Searches logs in a service by log type
    '''

    service = services_collection.find_one({"id": global_data.get("service_id"), "user_id": getattr(request, "auth_identity", None)})

    if not service:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", "service was not found", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": False, "message": "service not found", "status": 404}
    
    logs = logs_collection.find({"service_id": service["id"], "level": global_data.get("level")})

    logs_list = list(logs)

    if len(logs_list) == 0:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "info", "no logs were found", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": True, "message": "no logs found"}
    
    if len(logs_list) > 50:

        filtered_logs = logs_list[:50]

        return {"ok": True, "message": filtered_logs}
    else:

        return {"ok": True, "message": logs_list}





def search_logs_by_type_extra(global_data, services_collection, logs_collection, request):

    '''
        Searches for more logs by type in a service
    '''

    service = services_collection.find_one({"id": global_data.get("service_id"), "user_id": getattr(request, "auth_identity", None)})

    if not service:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "warning", "service was not found", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": False, "message": "service not found", "status": 404}
    
    logs = logs_collection.find({"service_id": service["id"], "level": global_data.get("level")})

    logs_list = list(logs)

    if len(logs_list) == 0:

        log(os.getenv("LOGARBOR_LOG_SERVICE_ID"), "info", "no logs were found", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": True, "message": "no logs found"}
    
    if len(logs_list) > global_data.get("extra"):

        filtered_logs = logs_list[:global_data.get("extra")]

        return {"ok": True, "message": filtered_logs}
    else:

        return {"ok": True, "message": logs_list}
    




def get_speed_log_ingection(services_collection, logs_collection, request):

    '''
        Gets the speed of logs coming to each service
    '''

    user_services = services_collection.find({"user_id": getattr(request, "auth_identity", None)})

    user_services_list = list(user_services)

    if len(user_services_list) == 0:

        return {"ok": True, "message": "no services"}

    speed_final_metric = []

    for service in user_services_list:

        services_logs = logs_collection.find({"service_id": service["id"]})

        services_logs_list = list(services_logs)

        now = datetime.datetime.today()

        recent_logs = [l for l in services_logs_list if (now - l["time"]).total_seconds() <= 10]

        speed = len(recent_logs) / 10

        metric_object = {"service_id": service["id"], "service_name": service["name"], "speed": speed}

        speed_final_metric.append(metric_object)
    
    return {"ok": True, "message": speed_final_metric}