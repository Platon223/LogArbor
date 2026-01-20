from log_arbor.utils import log 
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../../.env')

def check_ui_blueprint(logging_service_name, blueprint_actual, blueprint_expected, request):

    ''' 
        Checks if the route is being called through the /bl blueprint version
    '''

    if not blueprint_actual == blueprint_expected:

        log(os.getenv(f"LOGARBOR_{logging_service_name}_SERVICE_ID"), "warning", f"ui route was accessed with non ui blueprint: {request.path}", "ddcd3253-3d63-4254-9cbb-fc8531cef5f7")

        return {"ok": False, "message": "ui route only"}
    
    return {"ok": True}