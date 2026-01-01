from flask import request, Blueprint, render_template

guest_bl = Blueprint("guest_bl", __name__, template_folder="templates", static_folder="static")

@guest_bl.route("/", methods=["GET"])
def homepage():
    return render_template("homepage.html")