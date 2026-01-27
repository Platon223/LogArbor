from flask import request, Blueprint, render_template

guest_bl = Blueprint("guest_bl", __name__, template_folder="templates", static_folder="static", static_url_path="/guest-static")

@guest_bl.route("/", methods=["GET"])
def homepage():

    # Renders homepage.html

    return render_template("homepage.html")





@guest_bl.route("/docs", methods=["GET"])
def docs():

    # Renders docs.html

    return render_template("docs.html")





@guest_bl.route("/docs/<topic>", methods=["GET"])
def docs_topic(topic):

    # Renders a speciffic topic in docs

    return render_template(f"{topic}.html")


