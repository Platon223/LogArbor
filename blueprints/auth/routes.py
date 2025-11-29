from flask import Blueprint, request, Response
from dotenv import load_dotenv

load_dotenv()

auth_bl = Blueprint("auth_bl", __name__)

@auth_bl.route("/register", methods=["GET", "POST"])
def register():
    pass
