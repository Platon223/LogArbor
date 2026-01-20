from log_arbor.utils import log
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../../.env')

def get_settings(user_id, user_collection, request):

    '''
        Gets user's settings
    '''

    user = user_collection.find_one({"id": user_id})

    if not user:

        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "warning", f"user not found at {request.path} ({request.method})")

        return {"ok": False, "status": 404, "message": "user not found"}
    
    oauth_providers = ["Github User", "Google User"]
    
    settings_object = {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "account_type": user["account_type"],
        "auth_provider": "LogArbor" if not user["password"] in oauth_providers else user["password"]
    }

    return {"ok": True, "message": settings_object}