from flask import Flask, render_template, flash, redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm
import cv2

app = Flask(__name__)
app.config['SECRET_KEY'] = '92f3fc2bc60b51fa5bd949b418a6ddad'

#### Data Base ####
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# db = SQLAlchemy(app)

#### Static for tests #####
loggedIn = True;
username = 'admin'
password = 'admin'
admins = {'username': 'admin', 'password': 'admin'}
cameras = [
    {'name': 'Left view', 'status': 'active', 'src': 'https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1&mute=1&controls=0', 'date': '26/04/2023', 'hour': '14:50:00'},
    {'name': 'Top view', 'status': 'inactive', 'src': 'https://www.youtube.com/embed/Hy8kmNEo1i8?autoplay=1&mute=1&controls=0', 'date': '26/04/2023', 'hour': '14:50:00'},
    {'name': 'Right view', 'status': 'active', 'src': 'https://www.youtube.com/embed/k85mRPqvMbE?autoplay=1&mute=1&controls=0', 'date': '26/04/2023', 'hour': '14:50:00'}
    # {'name': 'Back view', 'status': 'inactive', 'src': 'static/video.mp4', 'date': '26/04/2023', 'hour': '14:50:00'},
    # {'name': 'Bottom view', 'status': 'inactive', 'src': 'static/video.mp4', 'date': '26/04/2023', 'hour': '14:50:00'},
    # {'name': 'Top view', 'status': 'active', 'src': 'static/video.mp4', 'date': '26/04/2023', 'hour': '14:50:00'}
]


def gen():
    cap = cv2.VideoCapture('rtsp://192.168.1.30:554/stream1')
    while True:
        ret, frame = cap.read()
        if ret:
            _, jpeg = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')



#### Flask Rooting Fonctions ####
@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == username and form.password.data == password:
            return redirect(url_for('home'))
        else:
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
