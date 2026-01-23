from log_arbor.utils import log 
import os

def check_ui_blueprint(blueprint_actual, blueprint_expected):

    ''' 
        Checks if the route is being called through the /bl blueprint version
    '''

    if not blueprint_actual == blueprint_expected:

        return {"ok": False, "message": "ui route only"}
    
    return {"ok": True}


def check_api_blueprint(blueprint_actual, blueprint_expected):

    ''' 
        Checks if the route is being called through the /api/v1 blueprint version
    '''

    if not blueprint_actual == blueprint_expected:

        return {"ok": False, "message": "api route only"}
    
    return {"ok": True}