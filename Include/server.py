############################################################
####----------------------------------------------------####
####   Camera streaming server concept for UiT Narvik   ####
####   Author : Loup RUSAK                              ####
####----------------------------------------------------####
############################################################

# If you want to change or add cameras :
#       Add sockets and bind sockets to differents tcp out port
#       Add the new urls of cameras to cam_urls array
#       Add video capture of the stream with the cam url
#       Create appropriate thread with own socket and stream, and start the thread
#       Remind to join the threads and release video capture


import zmq
import cv2
import threading

# Network and socket configuration
context = zmq.Context()

print("Creating sockets...")

# socket1 = context.socket(zmq.PUB)
# socket2 = context.socket(zmq.PUB)
# socket3 = context.socket(zmq.PUB)

# socket1 = context.socket(zmq.REQ)
# socket2 = context.socket(zmq.REQ)
# socket3 = context.socket(zmq.REQ)

socket1 = context.socket(zmq.PUSH)
socket2 = context.socket(zmq.PUSH)
socket3 = context.socket(zmq.PUSH)

cloud_server_sockets_ips = [
    'tcp://10.0.0.103:5555',
    'tcp://10.0.0.103:5556',
    'tcp://10.0.0.103:5557'
]

print("Binding sockets...")
# socket1.bind("tcp://*:5555")
# socket2.bind("tcp://*:5556")
# socket3.bind("tcp://*:5557")
socket1.connect(cloud_server_sockets_ips[0])
socket2.connect(cloud_server_sockets_ips[1])
socket3.connect(cloud_server_sockets_ips[2])

# Cameras configuration
local_cam_urls = [
    'rtsp://10.0.0.228:554/stream1',
    'rtsp://10.0.0.229:554/stream1',
    'rtsp://10.0.0.231:554/stream1'
]

# Video capture of cameras
print("Capturing video streams...")
cap1 = cv2.VideoCapture(local_cam_urls[0])
cap2 = cv2.VideoCapture(local_cam_urls[1])
cap3 = cv2.VideoCapture(local_cam_urls[2])

# Capture camera video and send it to client
def capture_send_video(socket, cap, n):
    print("Sending data cam"+str(n)+"...")
    while True:
        ret, frame = cap.read()
        # Encode frames
        encoded_frame = cv2.imencode('.jpg', frame)
        frame_data = encoded_frame[1].tobytes()
        topic = "cam"+str(n)
        # Send frames with topic
        socket.send_multipart([topic.encode(), frame_data])
        # socket.send(frame_data)
        # message = socket.recv()
        # print(message)

# Main Program
print("Creating threads...")
thread_cam_1 = threading.Thread(target=capture_send_video, args=(socket1,cap1,1))
thread_cam_2 = threading.Thread(target=capture_send_video, args=(socket2,cap2,2))
thread_cam_3 = threading.Thread(target=capture_send_video, args=(socket3,cap3,3))

print("Starting threads...")
thread_cam_1.start()
thread_cam_2.start()
thread_cam_3.start()

print("\nRunning...")

thread_cam_1.join()
thread_cam_2.join()
thread_cam_3.join()

cap1.release()
cap2.release()
cap3.release()

socket1.close()
socket2.close()
socket3.close()

context.term()