from flask import request, make_response, Blueprint, render_template
from flask_jwt_extended import jwt_required
from handlers.auth_check_wrapper import auth_check_wrapper

home_blp = Blueprint("home_blp", __name__, template_folder="templates", static_folder="static")

@home_blp.route("/dashboard/<user_id>", methods=["GET"])
def dashboard(user_id):
    return render_template("dashboard.html", user_id=user_id)


@home_blp.route("/credentials/username", methods=["POST"])
@auth_check_wrapper()
def username_info():
    user_identity = getattr(request, "auth_identity", None)
    return {"message": user_identity}