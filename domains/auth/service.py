from log_arbor.utils import log
import os
import uuid
import datetime
from validates.validate_db import validate_db_data
from db_schemas.users import users_schema
from db_schemas.verify_codes import verify_codes_schema
from db_schemas.jwt import jwt_schema
from extensions.bcrypt import bcrypt
from datetime import timedelta
import secrets
from handlers.email_verify import send_verification_email
from flask_jwt_extended import create_access_token, create_refresh_token
from flask import make_response, session
from extensions.oauth import github


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

    
    # Finds the user
        
    user = users_collection.find_one({"username": global_data.get("username")})

    if not user:

        log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "warning", f"user was not found at {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": False, "message": "user not found", "status": 404}

    
    # Checks the password
        
    if not bcrypt.check_password_hash(user["password"], global_data.get('password')):

        log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "warning", f"invalid password at {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": True, "message": "invalid password", "status": 401}

    
    # Checks if the user is remembered
    
    if user["remember"] and user["remember_expiration_date"] > datetime.datetime.today():

        log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "info", f"user remembered at {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": True, "message": "fetch for jwt"}

    
    # Sends a verification code

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

    # Checks if the email was sent

    if not result == "success":

        log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "critical", f"User: {user['username']} failed to receive verification code email", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": False, "message": f"something went wrong while sending an email: {result}", "status": 500}

    
    # Stores the verification code

    db_verify_code_data = {
        "id": str(uuid.uuid4()),
        "code": verification_code,
        "user_id": user["id"],
        "expiration_date": datetime.datetime.today() + timedelta(minutes=5)
    }
    
    db_verify_code_data_validate = validate_db_data(db_verify_code_data, verify_codes_schema)

    if "error" in db_verify_code_data_validate:

        log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "warning", f"user failed data validation on db_validate at: {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": False, "message": db_verify_code_data_validate, "status": 400}
        
    verify_codes_collection.insert_one(db_verify_code_data)

    return {"ok": True, "message": "redirect to verify", "user_id": user["id"], "remember": True if global_data.get("remember") else False}





def verify_account(global_data, verify_codes_collection, users_collection, request):

    '''
        Verifies user's account
    '''

    # Finds a verification code

    verify_code = verify_codes_collection.find_one({"code": global_data.get("code"), "user_id": global_data.get("user_id")})

    if not verify_code:

        log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "info", f"user provided an invalid verification code at: {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": False, "message": "invalid code", "status": 401}
    

    # Checks if the code is expired
        
    if verify_code["expiration_date"] < datetime.datetime.today():

        verify_codes_collection.delete_one({"id": verify_code["id"]})

        log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "info", f"user's verification code has been expired at: {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": False, "message": "expired", "status": 401}
    

    # Deletes the verification code
        
    verify_codes_collection.delete_one({"id": verify_code["id"]})


    # If user is remembered, remember the user
    
    if global_data.get("remember"):

        filter_query = {"id": global_data.get("user_id")}

        update_operation = {
            "$set": {
                "remember": True,
                "remember_expiration_date": datetime.datetime.today() + timedelta(minutes=5)
            }
        }

        users_collection.update_one(filter_query, update_operation)
    
    log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "info", f"user has been verified: {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

    return {"ok": True, "message": "verified"}





def jwt_credentials(global_data, jwt_collection, request):

    '''
        Gives the user jwt credentials
    '''

    # Creates access and refresh tokens

    access_token = create_access_token(identity=global_data.get("user_id"))

    refresh_token = create_refresh_token(identity=global_data.get("user_id"))


    # Stores the jwt object

    db_jwt_data = {
        "id": str(uuid.uuid4()),
        "token": refresh_token,
        "user_id": global_data.get("user_id")
    }

    db_jwt_validated_data = validate_db_data(db_jwt_data, jwt_schema)

    if "error" in db_jwt_validated_data:

        log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "warning", f"user failed data validation on db_validate at: {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": False, "message": db_jwt_validated_data, "status": 400}
            
    jwt_collection.insert_one(db_jwt_data)

    log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "warning", f"user has gotten their jwt tokens at: {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

    return {"ok": True, "message": "send credentials", "actk": access_token, "rftk": refresh_token}





def github_oauth(users_collection, request):

    '''
        Logs in the user with github oauth
    '''

    # Checks the access token

    try:

        token = github.authorize_access_token()
    except Exception as e:

        log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "critical", f"something went wrong at oauth with github at a callback at: {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": False, "message": "something went wrong", "status": 500}
    

    # Gets user's data

    user_data = github.get("user", token=token).json()

    emails_data = github.get("user/emails").json()

    primary_email = next(
        (e['email'] for e in emails_data if e['primary'] and e['verified']), 
        None
    )
    
    oauth_user = users_collection.find_one({"email": primary_email, "password": "Github User"})
    
    user_id = str(uuid.uuid4())


    # If user doesn't exist yet (first login) then create a user

    if not oauth_user:

        # Stores the user object

        db_data = {
            "id": user_id,
            "username": user_data.get("name"),
            "password": "Github User",
            "email": primary_email,
            "account_type": "Default",
            "remember": False,
            "remember_expiration_date": datetime.datetime.today()
        }

        db_validated_data = validate_db_data(db_data, users_schema)

        if "error" in db_validated_data:

            log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "critical", f"user failed data validation on db_validate at: {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

            return {"ok": False, "message": db_validated_data, "status": 400}
        
        users_collection.insert_one(db_data)

    
    # Sets sessions
        
    session["oauth_user"] = oauth_user["id"] if oauth_user else user_id

    session.permanent = True

    return {"ok": True, "message": "redirect to dashboard"}





def change_password(global_data, users_collection, request):

    '''
        Changes the user's password
    '''

    # Finds the user
        
    user = users_collection.find_one({"id": getattr(request, "auth_identity", None)})

    if not user:

        log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "warning", f"user was not found at {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": False, "message": "user not found", "status": 404}

    
    # Checks the password
        
    if not bcrypt.check_password_hash(user["password"], global_data.get('current_password')):

        log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "warning", f"invalid password at {request.path}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        return {"ok": True, "message": "invalid password", "status": 401}
    

    # Changes the password

    new_password = bcrypt.generate_password_hash(global_data.get("new_password"))

    filter_query = {"id": user["id"]}

    update_operation = {
        "$set": {
            "password": new_password
        }
    }

    users_collection.update_one(filter_query, update_operation)


    return {"ok": True, "message": "password updated"}

