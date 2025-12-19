from flask import request, make_response, Blueprint

home_bl = Blueprint("home_bl", __name__, template_folder="templates", static_folder="static")

