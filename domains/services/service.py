from log_arbor.utils import log
import os
import uuid
from validates.validate_db import validate_db_data
from db_schemas.services import services_schema


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

        log("AUTH", "warning", "user failed data validation on db_validate on /services/create")

        return {"message": db_data_validated}
        
    services_collection.insert_one(db_data)
    
    
    log("SERVICES", "info", "user created a services successfully")

    return {"message": "created"}