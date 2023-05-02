from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

loggedIn = True;

cameras = [
    {
        'name': 'Front view',
        'active': 'true',
        'src': 'cam-view.jpg',
        'date': '26/04/2023',
        'hour': '14:50:26'
    },
    {
        'name': 'Rear view',
        'active': 'false',
        'src': 'cam-view.jpg',
        'date': '26/04/2023',
        'hour': '14:50:26'
    },
    {
        'name': 'Top view',
        'active': 'true',
        'src': 'cam-view.jpg',
        'date': '26/04/2023',
        'hour': '14:50:26'
    },
    {
        'name': 'Left view',
        'active': 'false',
        'src': 'cam-view.jpg',
        'date': '26/04/2023',
        'hour': '14:50:26'
    },
    {
        'name': 'Right view',
        'active': 'true',
        'src': 'cam-view.jpg',
        'date': '26/04/2023',
        'hour': '14:50:26'
    },
    {
        'name': 'Bottom view',
        'active': 'false',
        'src': 'cam-view.jpg',
        'date': '26/04/2023',
        'hour': '14:50:26'
    },
]


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
        return render_template("all.html", title="All Cams", loggedIn=loggedIn, activetab='all', cameras=cameras)


@app.route("/settings")
def settings():
    if loggedIn:
        return render_template("settings.html", title="Settings", loggedIn=loggedIn)


@app.route("/")
def log_out():
    print('yes')
