from flask import Blueprint, request, Response, render_template, g, make_response, url_for, session, redirect
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from dotenv import load_dotenv
from validates.validate_api import validate_route
from validates.validate_db import validate_db_data
from extensions.mongo import mongo
from extensions.bcrypt import bcrypt
from db_schemas.users import users_schema
from db_schemas.jwt import jwt_schema
from db_schemas.verify_codes import verify_codes_schema
from validates.validate_db import validate_db_data
from pymongo.errors import DuplicateKeyError, OperationFailure, PyMongoError
from logg.log import log
import uuid
import secrets
import datetime
from handlers.email_verify import send_verification_email
import os
from datetime import timedelta
from extensions.oauth import github

load_dotenv()

auth_bl = Blueprint("auth_bl", __name__, template_folder="templates", static_folder="static")

@auth_bl.before_request
def data_validation():
    if request.method == "POST":
        path = request.path
        schema_name = path.replace("/auth/", "")
        data = validate_route(request, schema_name)
        if "error" in data:
            log("AUTH", "warning", f"user failed data validation on api_validate on {schema_name}")
            return {"message": data}, 400
        
        g.data = data
        
@auth_bl.before_request
def monitor():
    if not "/auth/static/" in request.path:
        monitor_data = {
            "request": request.method,
            "path": request.path,
            "data": request.get_json() if request.method == "POST" else "GET request"
        }

        try:
            mongo.db.monitoring.insert_one(monitor_data)
        except OperationFailure as e:
            log("AUTH", "critical", "failed inserting request data into monitor")
            return {"message": "something went wrong"}
        except PyMongoError as e:
            log("AUTH", "critical", "failed inserting request data into monitor, pymongo error")
            return {"message": "something went wrong"}
        except Exception as e:
            log("AUTH", "critical", "something went wrong while at the monitor middleware")
            return {"message": "something went wrong"}
    

@auth_bl.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        #validation process
        data = validate_route(request, "register")
        if "error" in data:
            log("AUTH", "warning", "user failed data validation on api_validate on register")
            return {"message": data}, 400
        db_data = {
            "id": str(uuid.uuid4()),
            "username": data.get("username"),
            "password": data.get("password"),
            "email": data.get("email"),
            "account_type": data.get("account_type"),
            "remember": False,
            "remember_expiration_date": datetime.datetime.today()
        }
        db_validated_data = validate_db_data(db_data, users_schema)
        if "error" in db_validated_data:
            log("AUTH", "warning", "user failed data validation on db_validate on register")
            return {"message": db_validated_data}, 400
        
        # finding/inserting process
        try:
            duplicated_user = mongo.db.users.find_one({"username": data.get("username")})
            if duplicated_user:
                log("AUTH", "info", "user tried using someone's username on register")
                return {"message": "username is already taken"}, 400
        except OperationFailure as e:
            log("AUTH", "critical", f"failed finding a duplicated user, for: {data.get('email')} on register")
            return {"message": f"error while finding the user: {e}"}, 500
        except PyMongoError as e:
            log("AUTH", "critical", f"failed finding a duplicated user, for: {data.get('email')} on register, pymongo error")
            return {"message": f"error with pymongo: {e}"}, 500
        
        try:
            db_data["password"] = bcrypt.generate_password_hash(data.get("password"))
            mongo.db.users.insert_one(db_validated_data)
        except DuplicateKeyError as e:
            log("AUTH", "critical", f"failed inserting a new user because duplicated, for: {data.get('email')}")
            return {"message": f"error duplicated user: {e}"}, 500
        except OperationFailure as e:
            log("AUTH", "critical", f"failed inserting a new user, for: {data.get('email')}")
            return {"message": f"error while inserting: {e}"}, 500
        except PyMongoError as e:
            log("AUTH", "critical", f"failed inserting a new user, for: {data.get('email')}, pymongo error")
            return {"message": f"error with pymongo: {e}"}, 500
        
        log("AUTH", "info", f"user: {data.get('username')} has been created")
        return {"message": f"user: {data.get('username')} has created an account"}, 200
    elif request.method == "GET":
        # GET request response
        return render_template("register.html")
    
@auth_bl.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        # validation process
        data = validate_route(request, "login")
        if "error" in data:
            log("AUTH", "warning", "user failed data validation on api_validate on login")
            return {"message": data}, 400
        
        # finding/inserting process
        try:
            user = mongo.db.users.find_one({"username": data.get("username")})
            if not user:
                log("AUTH", "info", "user was not found on login")
                return {"message": "user not found"}, 404
            
            if not bcrypt.check_password_hash(user["password"], data.get('password')):
                log("AUTH", "info", f"User: {data.get('username')} provided invalid password")
                return {"message": "invalid password"}, 401
        except OperationFailure as e:
            log("AUTH", "critical", f"failed finding a user, for: {data.get('username')}")
            return {"message": f"error while finding user: {e}"}, 500
        except PyMongoError as e:
            log("AUTH", "critical", f"failed finding a user, for: {data.get('username')}, pymongo error")
            return {"message": f"error with pymongo: {e}"}, 500
        except Exception as e:
            log("AUTH", "critical", "something went wrong")
            return {"message": "something went wrong"}, 500
        
        if user["remember"] and user["remember_expiration_date"] > datetime.datetime.today():
            log("AUTH", "info", f"User: {data.get('username')} was remembered and skipped the MFA process")
            return {"message": "fetch for jwt"}
    
        
        try:

            verification_code = str(secrets.randbelow(1000000)).zfill(6)

            result = send_verification_email(
                os.getenv("EMAILJS_SERVICE_ID"), 
                os.getenv("TEMPLATE_ID"),
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
            
            mongo.db.verify_codes.insert_one(db_verify_code_data)
        except OperationFailure as e:
            log("AUTH", "critical", f"failed inserting a verify code, for: {data.get('username')}")
            return {"message": f"error while finding user: {e}"}, 500
        except PyMongoError as e:
            log("AUTH", "critical", f"failed inserting a verify code, for: {data.get('username')}, error with pymongo")
            return {"message": f"error while finding user: {e}"}, 500
        except Exception as e:
            log("AUTH", "critical", "something went wrong")
            return {"message": f"something went wrong: {e}"}, 500
        
        log("AUTH", "info", f"User: {data.get('username')}, logged in and needs to be verified, user {'remembered' if data.get('remember') else 'not remembered'}")
        return {"message": "redirect to verify", "user_id": user["id"], "remember": True if data.get("remember") else False}, 200
    elif request.method == "GET":
        # GET request response
        return render_template("login.html")
    

@auth_bl.route("/verify", methods=["POST", "GET"])
def verify():
    if request.method == "POST":
        
        try:
            verify_code = mongo.db.verify_codes.find_one({"code": g.data.get("code"), "user_id": g.data.get("user_id")})
            if not verify_code:
                log("AUTH", "warning", f"User: {g.data.get('user_id')} provided an invalid verification code")
                return {"message": "invalid code"}, 401
            
            if verify_code["expiration_date"] < datetime.datetime.today():
                log("AUTH", "info", "user's verification code has been expired")
                return {"message": "expired"}, 401
            
            mongo.db.verify_codes.delete_one({"id": verify_code["id"]})
        except OperationFailure as e:
            log("AUTH", "critical", "failed while operating at verify")
            return {"message": "something went wrong"}, 500
        except PyMongoError as e:
            log("AUTH", "critical", "failed while operating at verify, pymongo error")
            return {"message": "something went wrong"}, 500
        except Exception as e:
            log("AUTH", "critical", "something went wrong at verify")
            return {"message": "something went wrong"}, 500
    
        
        
        try:
            if g.data.get("remember"):

                filter_query = {"id": g.data.get("user_id")}

                update_operation = {
                    "$set": {
                        "remember": True,
                        "remember_expiration_date": datetime.datetime.today() + timedelta(minutes=5)
                    }
                }

                mongo.db.users.update_one(filter_query, update_operation)
        except OperationFailure as e:
            log("AUTH", "critical", "failed while remembering the user at verify")
            return {"message": "something went wrong"}, 500
        except PyMongoError as e:
            log("AUTH", "critical", "failed while remembering the user at verify, pymongo error")
            return {"message": "something went wrong"}, 500
        except Exception as e:
            log("AUTH", "critical", "something went wrong while remembering the user at verify")
            return {"something went wrong"}, 500
        
        log("AUTH", "info", "user has been verified")
        return {"message": "verified"}, 200

    elif request.method == "GET":
        return render_template("verify.html")
    

@auth_bl.route("/jwt", methods=["POST"])
def jwt():

    access_token = create_access_token(identity=g.data.get("user_id"))
    refresh_token = create_refresh_token(identity=g.data.get("user_id"))

    try:

        db_jwt_data = {
            "id": str(uuid.uuid4()),
            "token": refresh_token,
            "user_id": g.data.get("user_id")
        }

        db_jwt_validated_data = validate_db_data(db_jwt_data, jwt_schema)
        if "error" in db_jwt_validated_data:
            log("AUTH", "warning", "user failed data validation on db_validate on verify")
            return {"message": db_jwt_validated_data}, 400
            
        mongo.db.jwt.insert_one(db_jwt_data)
    except OperationFailure as e:
        log("AUTH", "critical", "failed while inserting jwt at verify")
        return {"message": "something went wrong"}, 500
    except PyMongoError as e:
        log("AUTH", "critical", "failed while inserting jwt at verify, pymongo error")
        return {"message": "something went wrong"}, 500
    except Exception as e:
        log("AUTH", "critical", "something went wrong while inserting jwt at verify")
        return {"something went wrong"}, 500

    res = make_response({"message": "success"})
    res.set_cookie(
        "actk",
        access_token,
        max_age=timedelta(minutes=10).total_seconds(),
        secure=False,
        httponly=True,
        samesite="Lax"
    )
    res.set_cookie(
        "rftk",
        refresh_token,
        max_age=timedelta(hours=24).total_seconds(),
        secure=False,
        httponly=True,
        samesite="Lax"
    )
    log("AUTH", "info", "user has gotten their jwt tokens")
    return res, 200


@auth_bl.route("/oauth_github_login")
def github_login():
    redirect_uri = url_for("auth_bl.github_callback", _external=True)
    return github.authorize_redirect(redirect_uri)

@auth_bl.route("/oauth_github_callback")
def github_callback():

    try:

        token = github.authorize_access_token()
    except Exception as e:
        log("AUTH", "critical", f"something went wrong at oauth with github at a callback: {e}")
        return {"message": "something went wrong"}, 500

    user_data = github.get("user", token=token).json()
    emails_data = github.get("user/emails").json()

    primary_email = next(
        (e['email'] for e in emails_data if e['primary'] and e['verified']), 
        None
    )

    try:
        oauth_user = mongo.db.users.find_one({"email": primary_email, "password": "Github User"})
    except OperationFailure as e:
        log("AUTH", "critical", f"failed to find a user at oauth callback: {e}")
        return redirect("/auth/login?message=somethingwentwrong")
    except PyMongoError as e:
        log("AUTH", "critical", f"failed to find a user at oauth callback: {e}, pymongo error")
        return redirect("/auth/login?message=somethingwentwrong")
    except Exception as e:
        log("AUTH", "critical", f"something went wrong at oauth callback: {e}")
        return redirect("/auth/login?message=somethingwentwrong")
    
    user_id = str(uuid.uuid4())

    if not oauth_user:
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
            log("AUTH", "warning", "user failed data validation on db_validate on oauth callback")
            return {"message": db_validated_data}, 400
        

        try:
            oauth_user = mongo.db.users.insert_one(db_data)
        except OperationFailure as e:
            log("AUTH", "critical", f"failed to insert a user at oauth callback: {e}")
            return redirect("/auth/login?message=somethingwentwrong")
        except PyMongoError as e:
            log("AUTH", "critical", f"failed to insert a user at oauth callback: {e}, pymongo error")
            return redirect("/auth/login?message=somethingwentwrong")
        except Exception as e:
            log("AUTH", "critical", f"something went wrong at oauth callback: {e}")
            return redirect("/auth/login?message=somethingwentwrong")




    session["oauth_user"] = oauth_user["id"] if oauth_user else user_id
    session.permanent = True
    return redirect("/home/dashboard")

    

    
    
