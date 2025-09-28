# 📁 server.py -----

import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request

import db

app = Flask(__name__)

@app.before_request
def initialize():
    db.setup()

@app.route("/")
def index():
    guests = db.get_guests()
    return render_template("hello.html", guests=guests, session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

@app.route("/<name>")
def hello(name=None):
    return render_template("hello.html", name=name, guests=db.get_guests())

@app.route("/guestbook", methods=["POST"])
def guestbook():
    name = request.form["guest_name"]
    message = request.form["guest_message"]
    db.add_guest(name, message)
    return redirect("/")

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("index", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app.secret_key = env.get("APP_SECRET_KEY")

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))