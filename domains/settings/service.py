from log_arbor.utils import log
import os
from handlers.send_account_delete import send_account_delete_email

def get_settings(user_id, user_collection, request):

    '''
        Gets user's settings
    '''

    user = user_collection.find_one({"id": user_id})

    if not user:

        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "warning", f"user not found at {request.path} ({request.method})", "5b522faa-76a4-444c-8253-7f045f5c06af")

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

        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "warning", f"user not found at {request.path} ({request.method})", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"ok": False, "status": 404, "message": "user not found"}

    result = send_account_delete_email(os.getenv(""))

    if not result == "success":

        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "critical", f"user: {user["id"]} failed to recieve confirm delete account email", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"ok": False, "status": 500, "message": f"something went wrong while sending an email: {result}"}
    
    return {"ok": True, "message": "aproval email sent"}





def account_deletion(user_id, users_collection, global_data, request):

    ''' 
        Deletes user's account
    '''

    if not global_data("template_token") == os.getenv("APPROVE_ACCOUNT_DELETE_TOKEN"):

        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "warning", f"the template_token was invalid on /account_approve to delete an account: {user_id}", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"ok": False, "status": 401, "message": "invalid template token"}
    
    user = users_collection.find_one({"id": user_id})

    if not user:
        
        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "error", f"user was not found on: {request.path}", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"ok": False, "status": 404, "message": "user not found"}
    
    users_collection.delete_one({"id": user_id})
    
    return {"ok": True, "message": "deleted"}