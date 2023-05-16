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
loggedIn = True
username = 'admin'
password = 'admin'
admins = {'username': 'admin', 'password': 'admin'}

cam_urls = [
    'rtsp://192.168.1.30:554/stream1',
    'rtsp://192.168.1.30:554/stream2',
    'rtsp://192.168.1.30:554/stream3'
]

cameras = [
    {'name': 'Right View', 'status': '', 'src': 'video_feed_1', 'date': '', 'hour': ''},
    {'name': 'Top View', 'status': '', 'src': 'video_feed_2', 'date': '', 'hour': ''},
    {'name': 'Left View', 'status': '', 'src': 'video_feed_3', 'date': '', 'hour': ''}
]

def initCam(cam,url):
    print("avant")
    cap = cv2.VideoCapture(url)
    print("apres")
    if not cap.isOpened():
        print("cam inactive")
        cam['status'] = 'inactive'
    else:
        print("cam active")
        cam['status'] = 'active'
    #cam['src'] = url
    print("avant release")
    cap.release()
    print("apres release")

### TROP LONG A EXECUTER
def initCams():
    print("InitCams")
    for i in range(len(cam_urls)):
        initCam(cameras[i], cam_urls[i])

def gen_frames(url):
    print("GenFrames")
    cap = cv2.VideoCapture(url)

    while True:
        success, frame = cap.read()

        if not success:
            break
        else:
            # conversion de la frame en jpg
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # envoie de la frame vers la page html
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed_1')
def video_feed_1():
    # envoi du flux video 1
    return Response(gen_frames(cam_urls[0]), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_2')
def video_feed_2():
    # envoi du flux video 2
    return Response(gen_frames(cam_urls[1]), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_3')
def video_feed_3():
    # envoi du flux video 3
    return Response(gen_frames(cam_urls[2]), mimetype='multipart/x-mixed-replace; boundary=frame')



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
    initCams()
    if loggedIn:
        return render_template("home.html",
                               title="Home",
                               loggedIn=loggedIn,
                               activetab='home',
                               cameras=cameras)


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
