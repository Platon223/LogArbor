from flask import Blueprint, request, Response, render_template
from dotenv import load_dotenv
from validates.validate_api import validate_route
from validates.validate_db import validate_db_data
from extensions.mongo import mongo
from extensions.bcrypt import bcrypt
from db_schemas.users import users_schema
from db_schemas.verify_codes import verify_codes_schema
from validates.validate_db import validate_db_data
from pymongo.errors import DuplicateKeyError, OperationFailure, PyMongoError
from logg.log import log
import uuid
import secrets
import datetime

load_dotenv()

auth_bl = Blueprint("auth_bl", __name__, template_folder="templates", static_folder="static")

@auth_bl.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        #validation process
        data = validate_route(request, "register")
        if "error" in data:
            log("AUTH", "warning", "user failed data validation on api_validate on register")
            return {"message": data}, 400
        db_data = {
            "username": data.get("username"),
            "password": data.get("password"),
            "email": data.get("email"),
            "account_type": data.get("account_type")
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
            log("AUTH", "critical", f"failed finding a duplicated user, for: {data.get("email")} on register")
            return {"message": f"error while finding the user: {e}"}, 500
        except PyMongoError as e:
            log("AUTH", "critical", f"failed finding a duplicated user, for: {data.get("email")} on register, pymongo error")
            return {"message": f"error with pymongo: {e}"}, 500
        
        try:
            db_data["password"] = bcrypt.generate_password_hash(data.get("password"))
            db_data["id"] = str(uuid.uuid4())
            mongo.db.users.insert_one(db_validated_data)
        except DuplicateKeyError as e:
            log("AUTH", "critical", f"failed inserting a new user because duplicated, for: {data.get("email")}")
            return {"message": f"error duplicated user: {e}"}, 500
        except OperationFailure as e:
            log("AUTH", "critical", f"failed inserting a new user, for: {data.get("email")}")
            return {"message": f"error while inserting: {e}"}, 500
        except PyMongoError as e:
            log("AUTH", "critical", f"failed inserting a new user, for: {data.get("email")}, pymongo error")
            return {"message": f"error with pymongo: {e}"}, 500
        
        log("AUTH", "info", f"user: {data.get("username")} has been created")
        return {"message": f"user: {data.get("username")} has created an account"}, 200
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
            
            if not bcrypt.check_password_hash(user["password"], data.get("password")):
                log("AUTH", "info", f"User: {data.get("username")} provided invalid password")
                return {"message": "invalid password"}, 401
        except OperationFailure as e:
            log("AUTH", "critical", f"failed finding a user, for: {data.get("username")}")
            return {"message": f"error while finding user: {e}"}, 500
        except PyMongoError as e:
            log("AUTH", "critical", f"failed finding a user, for: {data.get("username")}, pymongo error")
            return {"message": f"error with pymongo: {e}"}, 500
        except Exception as e:
            log("AUTH", "critical", "something went wrong")
            return {"message": "something went wrong"}, 500
    
        
        try:
            db_verify_code_data = {
                "id": str(uuid.uuid4()),
                "code": str(secrets.randbelow(1000000)).zfill(6),
                "user_id": user["id"],
                "expiration_date": datetime.date.today()
            }
            db_verify_code_data_validate = validate_db_data(db_verify_code_data, verify_codes_schema)
            if "error" in db_verify_code_data_validate:
                log("AUTH", "warning", "user failed data validation on db_validate on login during verify code inserting")
                return {"message": db_verify_code_data_validate}, 400
            
            mongo.db.verify_codes.insert_one(db_verify_code_data)

        except OperationFailure as e:
            log("AUTH", "critical", f"failed inserting a verify code, for: {data.get("username")}")
            return {"message": f"error while finding user: {e}"}, 500
        except PyMongoError as e:
            log("AUTH", "critical", f"failed inserting a verify code, for: {data.get("username")}, error with pymongo")
            return {"message": f"error while finding user: {e}"}, 500
        except Exception as e:
            log("AUTH", "critical", "something went wrong")
            return {"message": "something went wrong"}, 500
        
        log("AUTH", "info", f"User: {data.get("username")}, logged in and needs to be verified, user {'remembered' if data.get("remember") else 'not remembered'}")
        return {"message": "redirect to verify"}, 200
    elif request.method == "GET":
        # GET request response
        return render_template("login.html")
    

    
    
