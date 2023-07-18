############################################################
####----------------------------------------------------####
####   Video Surveillance Flask Web App for UiT Narvik  ####
####   Author : Loup RUSAK                              ####
####----------------------------------------------------####
############################################################

from flask import Flask, render_template, flash, redirect, url_for, make_response, Response
from forms import LoginForm
import cv2
import numpy as np
import zmq
import time
import threading
from waitress import serve


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
cameras = [
    {'name': 'Right View', 'status': 'active', 'src': 'video_feed_1'},
    {'name': 'Top View', 'status': 'active', 'src': 'video_feed_2'},
    {'name': 'Left View', 'status': 'active', 'src': 'video_feed_3'}
]


###############################################################
#### ---------- ZMQ Client server configuration ---------- ####
###############################################################

# Sockets data
# Bind flask app sockets to server video streams sockets
# One for each camera
# Replace ip and port
# If just local : localhost
local_socket_ips = [
    "tcp://*:5555",
    "tcp://*:5556",
    "tcp://*:5557"
]

# Get ZMQ context
context = zmq.Context()

# Creation of sockets
print("Creating sockets...")
socket1 = context.socket(zmq.PULL)
socket2 = context.socket(zmq.PULL)
socket3 = context.socket(zmq.PULL)
socket1.setsockopt(zmq.RCVTIMEO,0)
socket2.setsockopt(zmq.RCVTIMEO,0)
socket3.setsockopt(zmq.RCVTIMEO,0)

# Connect sockets to server
print("Binding sockets...")
socket1.bind(local_socket_ips[0])
socket2.bind(local_socket_ips[1])
socket3.bind(local_socket_ips[2])


###########################################################
#### ---------- ZMQ / Flask Video Functions ---------- ####
###########################################################

last_visualization_time1 = None
last_visualization_time2 = None
last_visualization_time3 = None

def receive_encode_video(socket, last_visualisation_time):
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
            if last_visualisation_time is not None:
                elapsed_time = current_time - last_visualisation_time
                skipped_frames = int(elapsed_time / frame_time)
                for _ in range(skipped_frames):
                    try:
                        socket.recv_multipart(zmq.NOBLOCK)
                    except zmq.error.Again:
                        break
            last_visualisation_time = current_time
            # Send frame to html
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
            )
        except zmq.error.Again:
            time.sleep(frame_time)


@app.route('/video_feed_1')
def video_feed_1():
    response = make_response(receive_encode_video(socket1, last_visualization_time1))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.mimetype = 'multipart/x-mixed-replace; boundary=frame'
    return response

@app.route('/video_feed_2')
def video_feed_2():
    response = make_response(receive_encode_video(socket2, last_visualization_time2))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.mimetype = 'multipart/x-mixed-replace; boundary=frame'
    return response

@app.route('/video_feed_3')
def video_feed_3():
    response = make_response(receive_encode_video(socket3, last_visualization_time3))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.mimetype = 'multipart/x-mixed-replace; boundary=frame'
    return response


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
    #initCams()
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


###########################################################
#### ---------- Multithreading configuration --------- ####
###########################################################

# One thread per camera running receive and encode video
thread1 = threading.Thread(target=receive_encode_video, args=(socket1,last_visualization_time1))
thread2 = threading.Thread(target=receive_encode_video, args=(socket2,last_visualization_time2))
thread3 = threading.Thread(target=receive_encode_video, args=(socket3,last_visualization_time3))

thread1.start()
thread2.start()
thread3.start()

###########################################################
#### -------------- App configuration ---------------- ####
###########################################################

if __name__ == '__main__':
    # app.run(threaded=True)
    print("Running...")
    # Waitress server deployment configuration
    serve(app, host='0.0.0.0', port=8080, threads = 6)
