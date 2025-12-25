from flask import request, Blueprint, render_template, url_for, redirect, jsonify, g
from handlers.auth_check_wrapper import auth_check_wrapper
from logg.log import log
from validates.validate_api import validate_route
from validates.validate_db import validate_db_data
from db_schemas.services import services_schema
from pymongo.errors import DuplicateKeyError, OperationFailure, PyMongoError
from extensions.mongo import mongo
import uuid


services_bl = Blueprint("services_bl", __name__, template_folder="templates", static_folder="static")

@services_bl.before_request
def data_validation():
    if request.method == "POST":
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
            "alert_level": g.data.get("alert"),
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
                    f"{g.data.get("parameter")}": g.data.get("value")
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
    
    log("SERVICES", "info", f"user updated service: {g.data.get("service_id")} successufully")
    return {"message": "updated"}, 200

@services_bl.route("/delete_service", methods=["POST"])
@auth_check_wrapper()
def delete():
    try:
        mongo.db.services.delete_one({"id": g.data.get("service_id"), "user_id": getattr(request, "auth_identity", None)})
    except OperationFailure as e:
        log("SERVICES", "critical", f"failed deleting a service at /services/delete_service: {e}")
        return {"message": "something went wrong"}, 500
    except PyMongoError as e:
        log("SERVICES", "critical", f"failed deleting a service at /services/delete_service: {e}, pymongo error")
        return {"message": "something went wrong"}, 500
    except Exception as e:
        log("SERVICES", "critical", f"something went wrong at /services/delete_service: {e}")
        return {"message": "something went wrong"}, 500
    
    log("SERVICES", "info", f"user deleted a service: {g.data.get("service_id")} successufully")
    return {"message": "deleted"}, 200