import requests
from requests.exceptions import RequestException
import os
from dotenv import load_dotenv

load_dotenv()

def send_account_delete_email(service_id, template_id, public_key, access_token, name, from_param, email, message, user_id):

    try:
        email_json = {
            "service_id": service_id,
            "template_id": template_id,
            "user_id": public_key,
            "accessToken": access_token,
            "template_params": {
                "name": name,
                "email": email,
                "message": message,
                "from": from_param,
                "user_id": user_id
            }
        }
        response = requests.post(
            os.getenv("EMAILJS_SEND_API"),
            json=email_json,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            return "success"
        else:
            return response.text
    except RequestException as err:
        return f"request error: {err}"