############################################################
####----------------------------------------------------####
####   Video Surveillance Flask Web App for UiT Narvik  ####
####   Author : Loup RUSAK                              ####
####----------------------------------------------------####
############################################################

# If you want to add a camera to the website :
#       First add the camera to the sending server by following the instructions
#       Add the camera into "cameras" array with:
#           - Name of the camera you want to appear on the pages
#           - Status of the camera: "active" or "inactive"
#           - Name of the associated video_feed function.
#                   For example for the 4th camera : {'name':'XXX view', 'status':'inactive','src':'video_feed_4'}
#       Add a new local port for receiving new cam data from the server into "local_sockets_ip" array.
#       Add a new PULL socket and bind it to the right local listening port
#       Add a new "last_visualization_time" variable for new thread to create
#       Create a new "video_feed" function similar to the others
#       and in "make_response" add into the "receive_encode_video" function :
#           - The socket you created
#           - The last visualization time variable you created
#       Create a new thread running "receive_encode_video" function with:
#           - The socket you created
#           - The last visualization time variable you created
#       Start the created thread


from flask import Flask, render_template, flash, redirect, url_for, make_response
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
# If you want to add admins add a user to admins array and modify the login function
is_logged_in = False
username = 'admin'
password = 'admin'
admins = [{'username': 'admin', 'password': 'admin'}]

# Cameras data
# If you want to add a new camera add a cam into cameras array and bind the src to a video_feed function
# Also check the other requirements on the README.md file
cameras = [
    {'name': 'Right View', 'status': 'active', 'src': 'video_feed_1'},
    {'name': 'Top View', 'status': 'active', 'src': 'video_feed_2'},
    {'name': 'Left View', 'status': 'active', 'src': 'video_feed_3'}
]


###############################################################
#### ---------- ZMQ Client server configuration ---------- ####
###############################################################

# Sockets data
# Bind flask app sockets to local network ports
# One for each camera
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

# Bind sockets to local ips
print("Binding sockets...")
socket1.bind(local_socket_ips[0])
socket2.bind(local_socket_ips[1])
socket3.bind(local_socket_ips[2])


###########################################################
#### ---------- ZMQ / Flask Video Functions ---------- ####
###########################################################

# Last visualization time variables for recovering lost images in direct streams
# One per camera because of threads concurrency
last_visualization_time1 = None
last_visualization_time2 = None
last_visualization_time3 = None

#### Receive, decode and send video frames to the web page ####
# Threaded function
# Called one time per camera with binding socket and last visualization data
def receive_encode_video(socket, last_visualisation_time):
    frame_time = 0.0001
    while True:
        try:
            # Receiving bytes from server
            topic, data = socket.recv_multipart(zmq.NOBLOCK)
            # Bytes to frames
            np_data = np.frombuffer(data, np.uint8)
            decoded_frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
            encoded_frame = cv2.imencode('.jpg', decoded_frame)
            frame = encoded_frame[1].tobytes()
            # Skipping old frames and update to direct
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

#### Generate the camera 1 stream for th html page ####
@app.route('/video_feed_1')
def video_feed_1():
    response = make_response(receive_encode_video(socket1, last_visualization_time1))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.mimetype = 'multipart/x-mixed-replace; boundary=frame'
    return response

#### Generate the camera 2 stream for th html page ####
@app.route('/video_feed_2')
def video_feed_2():
    response = make_response(receive_encode_video(socket2, last_visualization_time2))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.mimetype = 'multipart/x-mixed-replace; boundary=frame'
    return response

#### Generate the camera 3 steream for th html page ####
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
        # Need to modify this if you want to add other admins
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

# Starting camera threads
thread1.start()
thread2.start()
thread3.start()

####################################################################
#### -------------- App Lunching configuration ---------------- ####
####################################################################

if __name__ == '__main__':
    # app.run(threaded=True)
    print("Running...")
    # Waitress server deployment configuration
    serve(app, host='0.0.0.0', port=8080, threads = 6)

    socket1.close()
    socket2.close()
    socket3.close()

    context.term()
