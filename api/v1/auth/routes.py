from flask import Blueprint, request, Response, render_template, g, make_response, url_for, session, redirect
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from validates.validate_api import validate_route
from validates.validate_db import validate_db_data
from extensions.mongo import mongo
from extensions.bcrypt import bcrypt
from db_schemas.users import users_schema
from db_schemas.jwt import jwt_schema
from db_schemas.verify_codes import verify_codes_schema
from validates.validate_db import validate_db_data
from pymongo.errors import DuplicateKeyError, OperationFailure, PyMongoError
import uuid
import secrets
import datetime
from handlers.email_verify import send_verification_email
from handlers.auth_check_wrapper import auth_check_wrapper
import os
from datetime import timedelta
from extensions.oauth import github
from log_arbor.utils import log
from domains.auth.service import register_account, login_account, verify_account, jwt_credentials, github_oauth, change_password
from extensions.limiter import limiter



auth_bl = Blueprint("auth_bl", __name__, template_folder="templates", static_folder="static")

@auth_bl.app_errorhandler(OperationFailure)
def handle_operation_failure(e):

    try:

        log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "critical", f"failed db operation at: {request.path} and error: {str(e)}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))
    except Exception as loge:

        return {"message": f"{loge}"}, 500
    
    return {"message": f"something went wrong: str(e)"}, 500





@auth_bl.app_errorhandler(PyMongoError)
def handle_operation_failure_pymongo(e):

    try:

        log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "critical", f"failed db operation at: {request.path} and error: {str(e)} because of a pymongo error", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))
    except Exception as loge:

        return {"message": f"{loge}"}, 500
    
    return {"message": f"something went wrong: {str(e)}"}, 500





@auth_bl.app_errorhandler(Exception)
def handle_operation_failure_exception(e):

    try:

        log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "critical", f"failed at: {request.path} and error: {e}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))
    except Exception as loge:

        return {"message": f"{loge}, log error"}, 500
    
    return {"message": f"something went wrong: {str(e)}"}, 500





@auth_bl.before_request
def data_validation():

    if request.method == "POST":

        path = request.path

        schema_name = path.replace("/auth/", "")

        data = validate_route(request, schema_name)

        if "error" in data:

            log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "warning", f"user failed data validation on api_validate on {schema_name}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))
            return {"message": data}, 400
        
        g.data = data



        
        
@auth_bl.route("/register", methods=["GET", "POST"])
@limiter.limit("3 per minute")
def register():

    if request.method == "POST":

        # Registers an account

        register_user_result = register_account(g.data, mongo.db.users, request)

        if not register_user_result["ok"]:

            return {"message": register_user_result["message"]}, register_user_result["status"]
        
        return {"message": register_user_result["message"]}, 200

    elif request.method == "GET":

        # Renders register.html

        return render_template("register.html")
    



    
@auth_bl.route("/login", methods=["POST", "GET"])
@limiter.limit("3 per minute")
def login():
    if request.method == "POST":

        # Cleans the previous session
        
        session.clear()

        # Login process

        login_result = login_account(g.data, mongo.db.users, mongo.db.verify_codes, request)

        if not login_result["ok"]:

            return {"message": login_result["message"]}, login_result["status"]
        
        if login_result["message"] == "redirect to verify":

            return {"message": login_result["message"], "user_id": login_result["user_id"], "remember": login_result["remember"]}, 200

    elif request.method == "GET":

        # Renders login.html

        return render_template("login.html")
    

@auth_bl.route("/verify", methods=["POST", "GET"])
@limiter.limit("3 per minute")
def verify():
    if request.method == "POST":
        
        # Verifies user's account

        verify_result = verify_account(g.data, mongo.db.verify_codes, mongo.db.users, request)

        if not verify_result["ok"]:

            return {"message": verify_result["message"]}, verify_result["status"]
        
        return {"message": verify_result["message"]}, 200

    elif request.method == "GET":

        # Renders verify.html

        return render_template("verify.html")
    

@auth_bl.route("/jwt", methods=["POST"])
@limiter.limit("3 per minute")
def jwt():

    # Gives the user JWT credentials

    jwt_result = jwt_credentials(g.data, mongo.db.jwt, request)

    if not jwt_result["ok"]:

        return {"message": jwt_result["message"]}, jwt_result["status"]
    
    if jwt_result["message"] == "send credentials":

        res = make_response({"message": "success"})

        res.set_cookie(
            "actk",
            jwt_result["actk"],
            max_age=timedelta(minutes=30).total_seconds(),
            secure=False,
            httponly=True,
            samesite="Lax"
        )

        res.set_cookie(
            "rftk",
            jwt_result["rftk"],
            max_age=timedelta(hours=24).total_seconds(),
            secure=False,
            httponly=True,
            samesite="Lax"
        )

        return res, 200


@auth_bl.route("/oauth_github_login")
@limiter.limit("3 per minute")
def github_login():

    # Redirects to github login

    redirect_uri = url_for("auth_bl.github_callback", _external=True)

    return github.authorize_redirect(redirect_uri)

@auth_bl.route("/oauth_github_callback")
def github_callback():

    # Logs user in with github oauth

    oauth_result = github_oauth(mongo.db.users, request)

    if not oauth_result["ok"]:

        return {"message": oauth_result["message"]}, oauth_result["status"]
    
    return redirect("/home/dashboard")

    

    
    
@auth_bl.route("/update_password", methods=["POST"])
@limiter.limit("3 per minute")
@auth_check_wrapper()
def new_password():

    # Changes user's password

    new_password_result = change_password(g.data, mongo.db.users, request)

    if not new_password_result["ok"]:

        return {"message": new_password_result["message"]}, new_password_result["status"]
    
    return {"message": new_password_result["message"]}, 200