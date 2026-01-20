from log_arbor.utils import log
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='../../../.env')

def account_deletion(user_id, users_collection, global_data, request):

    ''' 
        Deletes user's account
    '''

    if not global_data("template_token") == os.getenv("APPROVE_ACCOUNT_DELETE_TOKEN"):

        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "warning", f"the template_token was invalid on /account_approve to delete an account: {user_id}", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")

        return {"ok": False, "status": 401, "message": "invalid template token"}
    
    user = users_collection.find_one({"id": user_id})

    if not user:

        log(os.getenv("LOGARBOR_SETTINGS_SERVICE_ID"), "error", f"user was not found on: {request.path}", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")

        return {"ok": False, "status": 404, "message": "user not found"}
    
    users_collection.delete_one({"id": user_id})
    
    return {"ok": True, "message": "deleted"}