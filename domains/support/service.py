from log_arbor.utils import log
import os
from handlers.send_feedback_email import send_feedback_email
import re


def send_feedback(global_data, request):

    '''
        Sends feedback to LogArbor Support Team from a user
    '''

    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(email_pattern, global_data.get("email")):

        log(os.getenv("LOGARBOR_SUPPORT_SERVICE_ID"), "info", "user provided an invalid email when sending feedback", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"ok": False, "message": "invalid email", "status": 401}


    result = send_feedback_email(
        os.getenv("EMAILJS_SERVICE_ID"), 
        os.getenv("SEND_FEEDBACK_TEMPLATE_ID"),
        os.getenv("PUBLIC_EMAILJS_KEY"),
        os.getenv("ACCESS_TOKEN_EMAILJS"),
        "LogArbor Support Team",
        global_data.get("subject"),
        global_data.get("email"),
        global_data.get("message")
    )

    if not result == "success":

        log(os.getenv("LOGARBOR_SUPPORT_SERVICE_ID"), "critical", f"user: {getattr(request, "auth_identity", None)} failed to send a feedback email", "5b522faa-76a4-444c-8253-7f045f5c06af")

        return {"ok": False, "status": 500, "message": f"something went wrong while sending an email: {result}"}
    
    return {"ok": True, "message": "sent a feedback email"}

    