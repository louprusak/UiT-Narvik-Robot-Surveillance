############################################################
####----------------------------------------------------####
####   Video Surveillance Flask Web App for UiT Narvik  ####
####   Author : Loup RUSAK                              ####
####----------------------------------------------------####
############################################################

from flask import Flask, render_template, flash, redirect, url_for, Response
from forms import LoginForm
import cv2
import platform
import subprocess
from urllib.parse import urlparse
import numpy as np
import threading
import zmq


######################################################
#### ---------- App Configuration Data ---------- ####
######################################################

# App data
app = Flask(__name__)
app.config['SECRET_KEY'] = '92f3fc2bc60b51fa5bd949b418a6ddad'

# User login data
is_logged_in = False
username = 'admin'
password = 'admin'
admins = {'username': 'admin', 'password': 'admin'}

# Cameras data
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


###############################################################
#### ---------- ZMQ Client server configuration ---------- ####
###############################################################

# Sockets data
socket_ips = [
    "tcp://localhost:5555",
    "tcp://localhost:5556",
    "tcp://localhost:5557"
]
socket_topics = [
    b"cam1",
    b"cam2",
    b"cam3"
]

# Get ZMQ context
context = zmq.Context()

# Creation of sockets
print("Creating sockets...")
socket1 = context.socket(zmq.SUB)
socket2 = context.socket(zmq.SUB)
socket3 = context.socket(zmq.SUB)

# Connect sockets to server
print("Binding sockets...")
socket1.connect(socket_ips[0])
socket2.connect(socket_ips[1])
socket3.connect(socket_ips[2])

# Subscription to all topics
print("Sockets subscribing...")
socket1.setsockopt(zmq.SUBSCRIBE, socket_topics[0])
socket2.setsockopt(zmq.SUBSCRIBE, socket_topics[1])
socket3.setsockopt(zmq.SUBSCRIBE, socket_topics[2])


###########################################################
#### ---------- ZMQ / Flask Video Functions ---------- ####
###########################################################

#### Ping Util Fonction ####
def ping(host):
    param = '-n' if platform.system().lower()=='windows' else '-c'
    command = ['ping', param, '1', host]
    return subprocess.call(command) == 0

#### Status Init Cam ####
def initCam(cam,url):
    hostname = urlparse(url).hostname
    if ping(hostname):
        print("cam-active")
        cam['status'] = 'active'
    else:
        print("cam-inactive")
        cam['status'] = 'inactive'


#### Initialization of cams and status ####
def initCams():
    print("InitCams")
    for i in range(len(cam_urls)):
        initCam(cameras[i], cam_urls[i])

#### Receive decode and send video to html ####
def receive_display_video(socket):
    print("display video : "+str(socket))
    while True:
        # Receiving data from server
        topic, data = socket.recv_multipart()
        # data to frames
        np_data = np.frombuffer(data, np.uint8)
        decoded_frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
        encoded_frame = cv2.imencode('.jpg',decoded_frame)
        frame = encoded_frame[1].tobytes()
        # Send frame to html
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

#### Threaded function for generate cam1 frames ####
def gen_frames_cam1():
    print("gen frames 1")
    return receive_display_video(socket1)

#### Threaded function for generate cam2 frames ####
def gen_frames_cam2():
    print("gen frames 2")
    return receive_display_video(socket2)

#### Threaded function for generate cam3 frames ####
def gen_frames_cam3():
    print("gen frames 3")
    return receive_display_video(socket3)

#### Send cam1 video to html ####
@app.route('/video_feed_1')
def video_feed_1():
    # send cam 1 video to html
    return Response(gen_frames_cam1(), mimetype='multipart/x-mixed-replace; boundary=frame')

#### Send cam2 video to html ####
@app.route('/video_feed_2')
def video_feed_2():
    # send cam 2 video to html
    return Response(gen_frames_cam2(), mimetype='multipart/x-mixed-replace; boundary=frame')

#### Send cam3 video to html ####
@app.route('/video_feed_3')
def video_feed_3():
    # send cam =3 video to html
    return Response(gen_frames_cam3(), mimetype='multipart/x-mixed-replace; boundary=frame')


#####################################################################
#### ---------- Flask App Pages and Rooting Functions ---------- ####
#####################################################################

#### Login page rooting function (First page) ####
@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    global is_logged_in
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == username and form.password.data == password:
            is_logged_in = True
            return redirect(url_for('home'))
        else:
            is_logged_in = False
            flash('Login unsuccessful. Check username and password', 'danger')
    return render_template("login.html", title="Login", form=form)

#### Home page rooting function ####
@app.route("/home")
def home():
    initCams()
    if is_logged_in:
        return render_template("home.html",
                               title="Home",
                               activetab='home',
                               cameras = cameras)
    else:
        return redirect(url_for('login'))

#### Cams page rooting function ####
@app.route("/cams")
def cams():
    if is_logged_in:
        return render_template("cams.html",
                               title="Cams",
                               activetab='cams',
                               cameras=cameras)
    else:
        return redirect(url_for('login'))

#### All cam view page rooting function ####
@app.route("/all")
def all():
    if is_logged_in:
        return render_template("all.html",
                               title="All Cams",
                               activetab='all',
                               cameras=cameras)
    else:
        return redirect(url_for('login'))

#### Logout rooting function ####
@app.route("/logout")
def logout():
    global is_logged_in
    is_logged_in = False
    return redirect(url_for('login'))


############################################################
#### ---------- Multithreading Configuration ---------- ####
############################################################

# Creation of one thread per camera
print("Creating threads")
thread1 = threading.Thread(target=gen_frames_cam1)
thread2 = threading.Thread(target=gen_frames_cam2)
thread3 = threading.Thread(target=gen_frames_cam3)

# Starting all the threads
print("starting threads")
thread1.start()
thread2.start()
thread3.start()

# Waiting all threads to stop
thread1.join()
thread2.join()
thread3.join()