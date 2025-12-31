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
from handlers.auth_check_wrapper import auth_check_wrapper
from dotenv import load_dotenv

load_dotenv()

logs_bl = Blueprint("logs_bl", __name__, template_folder="templates", static_folder="static")

@logs_bl.before_request
def data_validation():
    if request.method == "POST" and not request.path == "/logs/all_logs":
        path = request.path
        data = validate_route(request, path)
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
    return render_template("logs.html")

@logs_bl.route("/add", methods=["POST"])
def add_log():
    try:
        service = mongo.db.services.find_one({"id": g.data.get("service_id")})
    except OperationFailure as e:
        log("LOGS", "critical", "failed finding a service at /logs/add")
        return {"message": "something went wrong"}, 500
    except PyMongoError as e:
        log("LOGS", "critical", "failed finding a service at /logs/add, pymongo error")
        return {"message": "something went wrong"}, 500
    except Exception as e:
        log("LOGS", "critical", "something went wrong at /logs/add")
        return {"message": "something went wrong"}, 500

    if not service:
        log("LOGS", "error", "service couldn't be found on /logs/add")
        return {"message": "service not found"}, 404
    

    time_format_string = "%Y-%m-%d %H:%M:%S"

    new_log_db_data = {
        "id": str(uuid.uuid4()),
        "service_id": service["id"],
        "message": g.data.get("message"),
        "level": g.data.get("level"),
        "time": datetime.strptime(g.data.get("time"), time_format_string)
    }

    db_validated_data = validate_db_data(new_log_db_data, logs_schema)
    if "error" in db_validated_data:
        log("LOGS", "warning", "user failed data validation on db_validate on /logs/add")
        return {"message": db_validated_data}, 400
    
    try:
        mongo.db.logs.insert_one(new_log_db_data)
    except OperationFailure as e:
        log("LOGS", "critical", "failed inserting a log at /logs/add")
        return {"message": "something went wrong"}, 500
    except PyMongoError as e:
        log("LOGS", "critical", "failed inserting a log at /logs/add, pymongo error")
        return {"message": "something went wrong"}, 500
    except Exception as e:
        log("LOGS", "critical", "something went wrong at /logs/add")
        return {"message": "something went wrong"}, 500
    
    return {"message": "logged"}, 200

@logs_bl.route("/all_logs", methods=["POST"])
@auth_check_wrapper()
def all_logs():
    try:
        services = mongo.db.services.find({"user_id": getattr(request, "auth_identity", None)})
    except OperationFailure as e:
        log("LOGS", "critical", "failed finding services at /logs/all_logs")
        return {"message": "something went wrong"}, 500
    except PyMongoError as e:
        log("LOGS", "critical", "failed finding services at /logs/all_logs, pymongo error")
        return {"message": "something went wrong"}, 500
    except Exception as e:
        log("LOGS", "critical", "something went wrong at /logs/all_logs")
        return {"message": "something went wrong"}, 500

    services_list = list(services)

    if len(services_list) == 0:
        log("LOGS", "info", "user has no services yet")
        return {"message": "no services"}, 404

    logs_list = []

    try:

        for service in services_list:
            service_logs = mongo.db.logs.find({"service_id": service["id"]})
            service_logs_list = list(service_logs)
            service_obj = {
                "service_id": service["id"],
                "service_name": service["name"], 
                "logs": service_logs_list
            }

            logs_list.append(service_obj)
    except OperationFailure as e:
        log("LOGS", "critical", "failed finding logs for service at /logs/all_logs")
        return {"message": "something went wrong"}, 500
    except PyMongoError as e:
        log("LOGS", "critical", "failed finding logs for service at /logs/all_logs, pymongo error")
        return {"message": "something went wrong"}, 500
    except Exception as e:
        log("LOGS", "critical", "something went wrong at /logs/all_logs")
        return {"message": "something went wrong"}, 500

    return {"message": logs_list}, 200