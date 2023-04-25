from flask import Flask, render_template, url_for
from jinja2 import tests

app = Flask(__name__)

loggedIn = True;

@app.route("/")
def login():
    return render_template("login.html", title="Login")

@app.route("/home")
def home():
    if loggedIn:
        return render_template("home.html", title="Home", loggedIn=loggedIn, activetab='home')

@app.route("/cams")
def cams():
    if loggedIn:
        return render_template("cams.html", title="Cams", loggedIn=loggedIn, activetab='cams')

@app.route("/all")
def all():
    if loggedIn:
        return render_template("all.html", title="All Cams", loggedIn=loggedIn, activetab='all')

@app.route("/settings")
def settings():
    if loggedIn:
        return render_template("settings.html", title="Settings", loggedIn=loggedIn)

@app.route("/")
def log_out():
    print('yes')

