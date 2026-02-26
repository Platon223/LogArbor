from log_arbor.utils import log
import os


def get_credentials(users_collection, request):

    '''
        Gets user's username
    '''

    user_identity = getattr(request, "auth_identity", None)

    current_user = users_collection.find_one({"id": user_identity})
    
    if not current_user:

        log(os.getenv("LOGARBOR_HOME_SERVICE_ID"), "warning", f"user was not found at {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": False, "message": "user not found", "status": 404}
    
    log(os.getenv("LOGARBOR_HOME_SERVICE_ID"), "info", "user got their credentials successufully", "6177b289-2b6f-44ea-a542-e2238263bd4e")

    return {"ok": True, "message": current_user["username"]}