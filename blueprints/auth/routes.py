from flask import Blueprint, request, Response
from dotenv import load_dotenv
from validates.validate_api import validate_route
from validates.validate_db import validate_db_data
from extensions.mongo import mongo
from db_schemas.users import users_schema
from validates.validate_db import validate_db_data
from pymongo.errors import DuplicateKeyError, OperationFailure, PyMongoError

load_dotenv()

auth_bl = Blueprint("auth_bl", __name__)

@auth_bl.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = validate_route(request, "register")
        if "error" in data:
            return {"message": data}, 400
        db_data = {
            "username": data.get("username"),
            "password": data.get("password"),
            "email": data.get("email"),
            "account_type": data.get("account_type")
        }
        db_validated_data = validate_db_data(db_data, users_schema)
        if "error" in db_validated_data:
            return {"message": db_validated_data}, 400
        
        try:
            duplicated_user = mongo.db.users.find_one({"username": data.get("username")})
            if duplicated_user:
                return {"message": "username is already taken"}, 400
        except OperationFailure as e:
            return {"message": f"error while finding the user: {e}"}, 500
        except PyMongoError as e:
            return {"message": f"error with pymongo: {e}"}, 500
        
        try:
            mongo.db.users.insert_one(db_validated_data)
        except DuplicateKeyError as e:
            return {"message": f"error duplicated user: {e}"}, 500
        except OperationFailure as e:
            return {"message": f"error while inserting: {e}"}, 500
        except PyMongoError as e:
            return {"message": f"error with pymongo: {e}"}, 500
        

        return {"message": f"user: {data.get("username")} has created an account"}, 200
    

    
    
