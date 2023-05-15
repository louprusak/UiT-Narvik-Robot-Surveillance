from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '92f3fc2bc60b51fa5bd949b418a6ddad'

#### Data Base ####
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# db = SQLAlchemy(app)

#### Static for tests #####
loggedIn = False
username = 'admin'
password = 'admin'
admins = {'username': 'admin', 'password': 'admin'}
cameras = [
    {'name': 'Left view', 'status': 'active', 'src': 'https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1&mute=1&controls=0', 'date': '26/04/2023', 'hour': '14:50:00'},
    {'name': 'Top view', 'status': 'inactive', 'src': 'https://www.youtube.com/embed/Hy8kmNEo1i8?autoplay=1&mute=1&controls=0', 'date': '26/04/2023', 'hour': '14:50:00'},
    {'name': 'Right view', 'status': 'active', 'src': 'https://www.youtube.com/embed/k85mRPqvMbE?autoplay=1&mute=1&controls=0', 'date': '26/04/2023', 'hour': '14:50:00'}
]


#### Flask Rooting Fonctions ####
@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    global loggedIn
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == username and form.password.data == password:
            print("Login ok")
            loggedIn = True
            return redirect(url_for('home'))
        else:
            print("login pas ok")
            loggedIn = False
            flash('Login unsuccessful. Check username and password', 'danger')
    return render_template("login.html", title="Login", form=form)


@app.route("/home")
def home():
    if loggedIn:
        return render_template("home.html",
                               title="Home",
                               loggedIn=loggedIn,
                               activetab='home',
                               cameras = cameras)
    else:
        return redirect(url_for('login'))

@app.route("/cams")
def cams():
    if loggedIn:
        return render_template("cams.html", title="Cams", loggedIn=loggedIn, activetab='cams', cameras=cameras)
    else:
        return redirect(url_for('login'))

@app.route("/all")
def all():
    if loggedIn:
        return render_template("all.html", title="All Cams", loggedIn=loggedIn, activetab='all', cameras=cameras)
    else:
        return redirect(url_for('login'))

# @app.route("/settings")
# def settings():
#     if loggedIn:
#         return render_template("settings.html", title="Settings", loggedIn=loggedIn)


@app.route("/logout")
def logout():
    global loggedIn
    print('deco')
    loggedIn = False
    return redirect(url_for('login'))
