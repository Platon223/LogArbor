from flask import request, make_response, Blueprint, render_template
from flask_jwt_extended import jwt_required

home_blp = Blueprint("home_blp", __name__, template_folder="templates", static_folder="static")

@home_blp.route("/dashboard", methods=["GET"])
@jwt_required
def dashboard():
    return render_template("dashboard.html")


@home_blp.route("/credentials/username", methods=["POST"])
@jwt_required
def username_info():
    pass