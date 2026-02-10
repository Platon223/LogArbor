from log_arbor.utils import log
import os


def get_alerts(alerts_collection, request):

    '''
        Gets user's alerts
    '''

    current_alerts = alerts_collection.find({"user_id": getattr(request, "auth_identity", None)})

    current_alerts_list = list(current_alerts)

    if len(current_alerts_list) == 0:

        return {"ok": True, "message": "no alerts"}
    
    return {"ok":True, "message": current_alerts_list}





def mark_alert_as_viewed(global_data, alerts_collection, request):

    '''
        Marks an alert as viewed
    '''

    alert = alerts_collection.find_one({"id": global_data.get("alert_id"), "user_id": getattr(request, "auth_identity", None)})

    if not alert:

        return {"ok": False, "message": "alert not found", "status": 404}
    
    filter_query = {"id": global_data.get("alert_id"), "user_id": getattr(request, "auth_identity", None)}

    update_operation = {
        "$set": {
            "viewed": global_data.get("status")
        }
    }

    alerts_collection.update_one(filter_query, update_operation)

    return {"ok": True, "message": "marked as viewed"}





def remove_alert(global_data, alerts_collection, request):

    '''
        Delete an alert
    '''

    alert = alerts_collection.find_one({"id": global_data.get("alert_id"), "user_id": getattr(request, "auth_identity", None)})

    if not alert:

        return {"ok": False, "message": "alert not found", "status": 404}
    
    alerts_collection.delete_one({"id": global_data.get("alert_id"), "user_id": getattr(request, "auth_identity", None)})

    return {"ok": True, "message": "deleted"}