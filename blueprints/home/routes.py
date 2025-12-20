from flask import request, make_response, Blueprint, render_template
from flask_jwt_extended import jwt_required

home_bl = Blueprint("home_bl", __name__, template_folder="templates", static_folder="static")

@home_bl.route("/dashboard", methods=["GET"])
@jwt_required
def dashboard():
    return render_template("dashboard.html")


@home_bl.route("/credentials/username", methods=["POST"])
@jwt_required
def username_info():
    pass