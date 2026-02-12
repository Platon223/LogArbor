from log_arbor.utils import log
import os
import uuid
import datetime
from validates.validate_db import validate_db_data
from db_schemas.users import users_schema
from db_schemas.verify_codes import verify_codes_schema
from extensions.bcrypt import bcrypt
from datetime import timedelta
import secrets
from handlers.email_verify import send_verification_email



def register_account(global_data, users_collection, request):

    '''
        Registers an account
    '''

    # Stores the user data in a dictionary

    db_data = {
        "id": str(uuid.uuid4()),
        "username": global_data.get("username"),
        "password": global_data.get("password"),
        "email": global_data.get("email"),
        "account_type": global_data.get("account_type"),
        "remember": False,
        "remember_expiration_date": datetime.datetime.today()
    }

    # Validates the structure and the contents of the user's data

    db_validated_data = validate_db_data(db_data, users_schema)

    # Handles an error while validating

    if "error" in db_validated_data:

        log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "info", f"user failed data validation at {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": False, "message": db_validated_data, "status": 401}
    
    # Avoids duplicated users
    
    duplicated_user = users_collection.find_one({"username": global_data.get("username")})

    if duplicated_user:

        log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "info", f"user tried using someone's username on register at {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": False, "message": "username is already taken", "status": 401}
    
    # Hashes the password
    
    db_data["password"] = bcrypt.generate_password_hash(global_data.get("password"))

    # Inserts the user

    users_collection.insert_one(db_validated_data)
    
    log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "info", f"user was created at {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

    return {"ok": True, "message": f"user: {global_data.get('username')} has created an account"}





def login_account(global_data, users_collection, verify_codes_collection, request):

    '''
        Log's the user in
    '''
        
    user = users_collection.find_one({"username": global_data.get("username")})

    if not user:

        log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "warning", f"user was not found at {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": False, "message": "user not found", "status": 404}
        
    if not bcrypt.check_password_hash(user["password"], global_data.get('password')):

        log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "warning", f"invalid password at {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": True, "message": "invalid password", "status": 401}
    
    if user["remember"] and user["remember_expiration_date"] > datetime.datetime.today():

        log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "info", f"user remembered at {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": True, "message": "fetch for jwt"}

    verification_code = str(secrets.randbelow(1000000)).zfill(6)

    result = send_verification_email(
        os.getenv("EMAILJS_SERVICE_ID"), 
        os.getenv("VERIFY_EMAIL_TEMPLATE_ID"),
        os.getenv("PUBLIC_EMAILJS_KEY"),
        os.getenv("ACCESS_TOKEN_EMAILJS"),
        user["username"],
        "LogArbor Support Team",
        user["email"],
        verification_code
    )

    if not result == "success":

        log("AUTH", "critical", f"User: {user['username']} failed to receive verification code email")

        return {"message": f"something went wrong while sending an email: {result}"}

    db_verify_code_data = {
        "id": str(uuid.uuid4()),
        "code": verification_code,
        "user_id": user["id"],
        "expiration_date": datetime.datetime.today() + timedelta(minutes=5)
    }
    
    db_verify_code_data_validate = validate_db_data(db_verify_code_data, verify_codes_schema)

    if "error" in db_verify_code_data_validate:

        log("AUTH", "warning", "user failed data validation on db_validate on login during verify code inserting")

        return {"message": db_verify_code_data_validate}, 400
        
    verify_codes_collection.insert_one(db_verify_code_data)
    
    log("AUTH", "info", f"User: {global_data.get('username')}, logged in and needs to be verified, user {'remembered' if global_data.get('remember') else 'not remembered'}")

    return {"message": "redirect to verify", "user_id": user["id"], "remember": True if global_data.get("remember") else False}, 200