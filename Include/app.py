############################################################
####----------------------------------------------------####
####   Video Surveillance Flask Web App for UiT Narvik  ####
####   Author : Loup RUSAK                              ####
####----------------------------------------------------####
############################################################

from flask import Flask, render_template, flash, redirect, url_for, make_response, Response
from forms import LoginForm
import cv2
import platform
import subprocess
from urllib.parse import urlparse
import numpy as np
import threading
import zmq
import time
import VideoStreamThread
from queue import Queue


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
    'rtsp://10.0.0.30:554/stream1',
    'rtsp://10.0.0.31:554/stream1',
    'rtsp://10.0.0.32:554/stream1'
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
socket1.setsockopt(zmq.RCVTIMEO,0)
socket2.setsockopt(zmq.RCVTIMEO,0)
socket3.setsockopt(zmq.RCVTIMEO,0)

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

last_visualization_time1 = None
last_visualization_time2 = None
last_visualization_time3 = None


    # # Creation of one thread per camera
    # print("INIT - Creating threads...")
    # thread1 = threading.Thread(target=generate_frames)
    # thread2 = threading.Thread(target=gen_frames_cam2)
    # thread3 = threading.Thread(target=gen_frames_cam3)
    #
    # # Starting all the threads
    # print("INIT - starting threads...")
    # thread1.start()
    # thread2.start()
    # thread3.start()
    #
    # # Waiting all threads to stop
    # # thread1.join()
    # # thread2.join()
    # # thread3.join()


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


def receive_encode_video(socket):
    global last_visualization_time1
    frame_time = 0.0001
    while True:
        try:
            # Receiving data from server
            topic, data = socket.recv_multipart(zmq.NOBLOCK)
            # Data to frames
            np_data = np.frombuffer(data, np.uint8)
            decoded_frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
            encoded_frame = cv2.imencode('.jpg', decoded_frame)
            frame = encoded_frame[1].tobytes()
            # Update when leaving and come back
            current_time = time.time()
            if last_visualization_time1 is not None:
                elapsed_time = current_time - last_visualization_time1
                skipped_frames = int(elapsed_time / frame_time)
                for _ in range(skipped_frames):
                    try:
                        socket.recv_multipart(zmq.NOBLOCK)
                    except zmq.error.Again:
                        break
            last_visualization_time1 = current_time
            # Send frame to html
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
            )
        except zmq.error.Again:
            time.sleep(frame_time)

@app.route('/video_feed_1')
def video_feed_1():
    return Response(receive_encode_video(socket1), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed_2')
def video_feed_2():
    # thread = threading.Thread(target=receive_encode_video, args=(socket2,))
    # thread.start()
    return Response(receive_encode_video(socket2), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_3')
def video_feed_3():
    # thread = threading.Thread(target=receive_encode_video, args=(socket3,))
    # thread.start()
    return Response(receive_encode_video(socket3), mimetype='multipart/x-mixed-replace; boundary=frame')



#### Receive decode and send video to html ####
# def receive_display_video(socket):
#     print("display video : "+str(socket))
#     i=1
#     while True:
#         print("socket : "+str(socket)+" ,frame : "+str(i))
#         # Receiving data from server
#         topic, data = socket.recv_multipart()
#         # data to frames
#         np_data = np.frombuffer(data, np.uint8)
#         decoded_frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
#         encoded_frame = cv2.imencode('.jpg',decoded_frame)
#         frame = encoded_frame[1].tobytes()
#         i=i+1
#         # Send frame to html
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#         time.sleep(0.01)
#
# #### Threaded function for generate cam1 frames ####
# def gen_frames_cam1():
#     print("gen frames 1")
#     return receive_display_video(socket1)
#
# #### Threaded function for generate cam2 frames ####
# def gen_frames_cam2():
#     print("gen frames 2")
#     return receive_display_video(socket2)
#
# #### Threaded function for generate cam3 frames ####
# def gen_frames_cam3():
#     print("gen frames 3")
#     return receive_display_video(socket3)
#
# #### Send cam1 video to html ####
# @app.route('/video_feed_1')
# def video_feed_1():
#     # send cam 1 video to html
#     response = make_response(gen_frames_cam1())
#     response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
#     response.headers['Pragma'] = 'no-cache'
#     response.headers['Expires'] = '0'
#     response.mimetype = 'multipart/x-mixed-replace; boundary=frame'
#     return response
#
# #### Send cam2 video to html ####
# @app.route('/video_feed_2')
# def video_feed_2():
#     # send cam 2 video to html
#     response = make_response(gen_frames_cam2())
#     response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
#     response.headers['Pragma'] = 'no-cache'
#     response.headers['Expires'] = '0'
#     response.mimetype = 'multipart/x-mixed-replace; boundary=frame'
#     return response
#
# #### Send cam3 video to html ####
# @app.route('/video_feed_3')
# def video_feed_3():
#     # send cam =3 video to html
#     response = make_response(gen_frames_cam3())
#     response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
#     response.headers['Pragma'] = 'no-cache'
#     response.headers['Expires'] = '0'
#     response.mimetype = 'multipart/x-mixed-replace; boundary=frame'
#     return response


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



