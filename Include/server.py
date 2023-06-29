#
#   Camera Video Publisher Server in Python
#   Binds PUB socket to tcp://*:5555
#
import datetime

import zmq
import cv2
import threading

# Network and socket configuration
context = zmq.Context()
print("Creating sockets...")
socket1 = context.socket(zmq.PUB)
socket2 = context.socket(zmq.PUB)
socket3 = context.socket(zmq.PUB)
print("Binding sockets...")
socket1.bind("tcp://*:5555")
socket2.bind("tcp://*:5556")
socket3.bind("tcp://*:5557")

# Cameras configuration
cam_urls = [
    'rtsp://10.0.0.30:554/stream1',
    'rtsp://10.0.0.31:554/stream1',
    'rtsp://10.0.0.32:554/stream1'
]

# Video capture of cameras
print("Capturing video streams...")
# print("before capture: " + str(datetime.datetime.now()))
cap1 = cv2.VideoCapture(cam_urls[0])
cap2 = cv2.VideoCapture(cam_urls[1])
cap3 = cv2.VideoCapture(cam_urls[2])
# print("after capture: " + str(datetime.datetime.now()))

# Capture camera video and send it to client
def capture_send_video(socket, cap, n):
    print("Sending data cam"+str(n)+"...")
    while True:
        ret, frame = cap.read()
        # print(str(n) + " (read): " + str(datetime.datetime.now()))
        # Encode frames
        encoded_frame = cv2.imencode('.jpg', frame)
        frame_data = encoded_frame[1].tobytes()
        # print(str(n) + " (encode): " + str(datetime.datetime.now()))
        topic = "cam"+str(n)
        # Send frames with topic
        socket.send_multipart([topic.encode(), frame_data])
        # print(str(n) + " (send): " + str(datetime.datetime.now()))

# Main Program
print("Creating threads...")
thread_cam_1 = threading.Thread(target=capture_send_video, args=(socket1,cap1,1))
thread_cam_2 = threading.Thread(target=capture_send_video, args=(socket2,cap2,2))
thread_cam_3 = threading.Thread(target=capture_send_video, args=(socket3,cap3,3))

print("Starting threads...")
thread_cam_1.start()
thread_cam_2.start()
thread_cam_3.start()

thread_cam_1.join()
thread_cam_2.join()
thread_cam_3.join()

cap1.release()
cap2.release()
cap3.release()