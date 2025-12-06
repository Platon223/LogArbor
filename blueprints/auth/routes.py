from flask import Blueprint, request, Response, render_template
from dotenv import load_dotenv
from validates.validate_api import validate_route
from validates.validate_db import validate_db_data
from extensions.mongo import mongo
from extensions.bcrypt import bcrypt
from db_schemas.users import users_schema
from validates.validate_db import validate_db_data
from pymongo.errors import DuplicateKeyError, OperationFailure, PyMongoError
from logg.log import log

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
            return {"message": data}
        
        # finding/inserting process
        try:
            user = mongo.db.users.find_one({"username": data.get("username")})
            if not user:
                log("AUTH", "info", "user was not found on login")
                return {"message": "user not found"}
            
            if not bcrypt.check_password_hash(user["password"], data.get("password")):
                log("AUTH", "info", f"User: {data.get("username")} provided invalid password")
                return {"message": "invalid password"}
        except OperationFailure as e:
            log("AUTH", "critical", f"failed finding a user, for: {data.get("username")}")
            return {"message": f"error while finding user: {e}"}
        except PyMongoError as e:
            log("AUTH", "critical", f"failed finding a user, for: {data.get("username")}, pymongo error")
            return {"message": f"error with pymongo: {e}"}
        except Exception as e:
            log("AUTH", "critical", "something went wrong")
            return {"message": "something went wrong"}
    
        
        try:
            pass
        except OperationFailure as e:
            pass
    elif request.method == "GET":
        # GET request response
        return render_template("login.html")
    

    
    
