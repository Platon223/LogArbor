from log_arbor.utils import log
import os


def get_credentials(users_collection, request):

    '''
        Gets user's username
    '''

    user_identity = getattr(request, "auth_identity", None)

    current_user = users_collection.find_one({"id": user_identity})
    
    if not current_user:

        log(os.getenv("LOGARBOR_HOME_SERVICE_ID"), "warning", f"user was not found at {request.path}", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"ok": False, "message": "user not found", "status": 404}
    
    log("tbd", "info", "user got their credentials successufully", "5b522faa-76a4-444c-8253-7f045f5c06af")

    return {"ok": True, "message": current_user["username"]}