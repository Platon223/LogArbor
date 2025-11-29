from flask import Blueprint, request, Response
from dotenv import load_dotenv
from validates.validate_api import validate_route
from validates.validate_db import validate_db_data
from extensions.mongo import mongo

load_dotenv()

auth_bl = Blueprint("auth_bl", __name__)

@auth_bl.route("/register", methods=["GET", "POST"])
def register():
    data = validate_route(request, "register")
    if "error" in data:
        return {"message": data}
    
    
    
    
