from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '92f3fc2bc60b51fa5bd949b418a6ddad'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

loggedIn = True;

admins = {'username':'admin','password':'admin'}

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


@app.route("/", methods=['GET','POST'])
@app.route("/login", methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == 'admin' and form.password.data == 'admin':
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Check username and password','danger')
    return render_template("login.html", title="Login", form = form)


@app.route("/home")
def home():
    if loggedIn:
        return render_template("home.html",
                               title="Home",
                               loggedIn=loggedIn,
                               activetab='home')


@app.route("/cams")
def cams():
    if loggedIn:
        return render_template("cams.html", title="Cams", loggedIn=loggedIn, activetab='cams', cameras=cameras)


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
