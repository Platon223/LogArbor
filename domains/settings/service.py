from log_arbor.utils import log
import os
from handlers.send_account_delete import send_account_delete_email

def get_settings(user_id, user_collection, request):

    '''
        Gets user's settings
    '''

    user = user_collection.find_one({"id": user_id})

    if not user:

        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "warning", f"user not found at {request.path} ({request.method})", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

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





def request_account_deletion(user_id, users_collection, request):

    '''
        Sends a verification email to delete an email
    '''

    user = users_collection.find_one({"id": user_id})

    if not user:

        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "warning", f"user not found at {request.path} ({request.method})", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": False, "status": 404, "message": "user not found"}

    result = send_account_delete_email(os.getenv("EMAILJS_SERVICE_ID"), os.getenv("SEND_ACCOUNT_DELETE_EMAIL_TEMPLATE_ID"), os.getenv("PUBLIC_EMAILJS_KEY"), os.getenv("ACCESS_TOKEN_EMAILJS"), user["username"], "LogArbor Support Team", user["email"], "message", user["id"])

    if not result == "success":

        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "critical", f"user: {user["id"]} failed to recieve confirm delete account email", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": False, "status": 500, "message": f"something went wrong while sending an email: {result}"}
    
    return {"ok": True, "message": "aproval email sent"}





def account_deletion(user_id, users_collection, logs_collection, services_collection, alerts_collection, jwt_collection, verify_codes_collection, request):

    ''' 
        Deletes user's account
    '''
    
    user = users_collection.find_one({"id": user_id})

    if not user:
        
        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "error", f"user was not found on: {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": False, "status": 404, "message": "user not found"}
    
    # Deletion proccess
    
    users_collection.delete_one({"id": user_id})
    logs_collection.delete({"user_id": user_id})
    services_collection.delete({"user_id": user_id})
    alerts_collection.delete({"user_id": user_id})
    jwt_collection.delete({"user_id": user_id})
    verify_codes_collection.delete({"user_id": user_id})
    
    return {"ok": True, "message": "redirect"}