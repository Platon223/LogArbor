from flask import request, make_response, Blueprint, render_template
from flask_jwt_extended import jwt_required
from handlers.auth_check_wrapper import auth_check_wrapper
from pymongo.errors import DuplicateKeyError, OperationFailure, PyMongoError
from logg.log import log
from extensions.mongo import mongo

home_blp = Blueprint("home_blp", __name__, template_folder="templates", static_folder="static")

@home_blp.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template("dashboard.html")


@home_blp.route("/credentials/username", methods=["POST"])
@auth_check_wrapper()
def username_info():
    user_identity = getattr(request, "auth_identity", None)

    try:
        current_user = mongo.db.users.find_one({"id": user_identity})
    except OperationFailure as e:
        log("DASHBOARD", "critical", f"failed to find a user at credentials/username: {e}")
        return {"message": "something went wrong"}, 500
    except PyMongoError as e:
        log("DASHBOARD", "critical", f"failed to find a user at credentials/username: {e}, pymongo error")
        return {"message": "something went wrong"}, 500
    except Exception as e:
        log("DASHBOARD", "critical", f"something went wrong at credentials/username: {e}")
        return {"message": "something went wrong"}, 500
    
    if not current_user:
        log("DASHBOARD", "warning", "user was not found at credentials/username")
        return {"message": "user not found"}, 404
    
    return {"message": current_user["username"]}, 200


