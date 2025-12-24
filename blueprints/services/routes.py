from flask import request, Blueprint, render_template, url_for, redirect, jsonify
from handlers.auth_check_wrapper import auth_check_wrapper


services_bl = Blueprint("services_bl", __name__, template_folder="templates", static_folder="static")

@services_bl.route("/create", methods=["POST"])
@auth_check_wrapper()
def create():
    pass


@services_bl.route("/update_service", methods=["POST"])
@auth_check_wrapper()
def update():
    pass

@services_bl.route("/delete_service", methods=["POST"])
@auth_check_wrapper()
def delete():
    pass
