from log_arbor.utils import log
import os


def get_credentials(users_collection, request):

    '''
        Gets user's username
    '''

    user_identity = getattr(request, "auth_identity", None)

    current_user = users_collection.find_one({"id": user_identity})
    
    if not current_user:

        log(os.getenv("LOGARBOR_HOME_SERVICE_ID"), "warning", f"user was not found at {request.path}", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")

        return {"ok": False, "message": "user not found", "status": 404}
    
    log(os.getenv("LOGARBOR_HOME_SERVICE_ID"), "info", "user got their credentials successufully", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")

    return {"ok": True, "message": current_user["username"]}