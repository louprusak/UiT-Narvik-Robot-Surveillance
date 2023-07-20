############################################################
####----------------------------------------------------####
####   Camera streaming server concept for UiT Narvik   ####
####   Author : Loup RUSAK                              ####
####----------------------------------------------------####
############################################################

# If you want to add a camera :
#       Add a cloud server ip and port for the new camera stream in "cloud_server_sockets_ips" array.
#       Add the local cam stream url to the "local_cam_urls" array.
#       Add a new PUSH socket and connect this socket to the right cloud server socket ip
#       Capture the video stream of the camera with cam url
#       Create a new thread running "capture_send_video" function with:
#           - The associated socket
#           - The assiciated video capture
#           - The numero of the camera for the creation of the topic
#       Start the created thread
#       Join the created thread for terminate
#       Release the video capture of the camera
#       Close the associated socket

import zmq
import cv2
import threading

# Get ZMQ Context
context = zmq.Context()

# Cloud server sockets ips to send the video streams
cloud_server_sockets_ips = [
    'tcp://20.100.204.66:5555',
    'tcp://20.100.204.66:5556',
    'tcp://20.100.204.66:5557'
]

# Local urls of the cameras for server video capture
local_cam_urls = [
    'rtsp://10.0.0.228:554/stream1',
    'rtsp://10.0.0.229:554/stream1',
    'rtsp://10.0.0.231:554/stream1'
]

# Creation of send sockets
print("Creating sockets...")
socket1 = context.socket(zmq.PUSH)
socket2 = context.socket(zmq.PUSH)
socket3 = context.socket(zmq.PUSH)

# Connecting sockets with cloud sockets
print("Binding sockets...")
socket1.connect(cloud_server_sockets_ips[0])
socket2.connect(cloud_server_sockets_ips[1])
socket3.connect(cloud_server_sockets_ips[2])

# Video capture of cameras
print("Capturing video streams...")
cap1 = cv2.VideoCapture(local_cam_urls[0])
cap2 = cv2.VideoCapture(local_cam_urls[1])
cap3 = cv2.VideoCapture(local_cam_urls[2])


#### Capture camera video and send it to client ####
# Threaded function
# Called one time per camera with send socket and camera video capture
def capture_send_video(socket, cap, n):
    print("Sending data cam"+str(n)+"...")
    while True:
        ret, frame = cap.read()
        if ret:
            # Encode frames
            encoded_frame = cv2.imencode('.jpg', frame)
            frame_data = encoded_frame[1].tobytes()
            topic = "cam"+str(n)
            # Send frames with topic
            socket.send_multipart([topic.encode(), frame_data])

# Creation of threads
# One per camera
print("Creating threads...")
thread_cam_1 = threading.Thread(target=capture_send_video, args=(socket1,cap1,1))
thread_cam_2 = threading.Thread(target=capture_send_video, args=(socket2,cap2,2))
thread_cam_3 = threading.Thread(target=capture_send_video, args=(socket3,cap3,3))

# Start the threads
print("Starting threads...")
thread_cam_1.start()
thread_cam_2.start()
thread_cam_3.start()

# Join the threads when terminate
print("\nRunning...")
thread_cam_1.join()
thread_cam_2.join()
thread_cam_3.join()

# Realease the video captures
cap1.release()
cap2.release()
cap3.release()

# Close the sockets
socket1.close()
socket2.close()
socket3.close()

# Terminate the ZMQ context
context.term()