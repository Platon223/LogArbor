from log_arbor.utils import log
from dotenv import load_dotenv
import os
from handlers.send_account_delete import send_account_delete_email

load_dotenv(dotenv_path='../../../.env')

def request_account_deletion(user_id, users_collection, request):

    '''
        Sends a verification email to delete an email
    '''

    user = users_collection.find_one({"id": user_id})

    if not user:

        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "warning", f"user not found at {request.path} ({request.method})", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")

        return {"ok": False, "status": 404, "message": "user not found"}

    result = send_account_delete_email(os.getenv(""))

    if not result == "success":

        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "critical", f"user: {user["id"]} failed to recieve confirm delete account email", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")

        return {"ok": False, "status": 500, "message": f"something went wrong while sending an email: {result}"}
    
    return {"ok": True, "message": "aproval email sent"}