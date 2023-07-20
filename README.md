# UiT-Narvik-Robot-Surveillance
---
Web based view for lab's robot surveillance cameras.

*Uses a server to video capture the camera streams and send it to the website server using ZMQ.*
*The flask web app gets this streams from the server and display it in different ways.*

*Need to configure sockets option and bindings for sending and receiving.*

**Made with Python 3.8**

---
## Python packages to install before : 
- Flask 2.3.2 : `pip install flask`
- Flask-WTF 1.1.1 : `pip install flask-wtf`
- OpenCv 2 : `pip install opencv-python`
- ZMQ 25.1.0 : `pip install pyzmq`
- Waitress 2.1.2 : `pip install waitress`

---
## Modify the urls and sockets : 
You need to modify the cameras urls and data and also the sockets urls and options to fit to your network setup.

### Server side (server.py) :
1. Modify the cloud server sockets ips to connect in the **"cloud_server_sockets_ips"** array.
2. Modify local cameras url to get video streams in the **"local_cam_urls"** array.

### Client side (app.py) : 
1. Modify the local sockets ips for receiving data in the **"local_socket_ips"** array.
2. On the app lunching configuration section, modify the host, port and threads number in the **serve** function.

---
## Add a camera to the website : 
if you want to add or remove some cameras or streams, you need to modify server and client configuration.
You need to add ip adresses, cameras data, sockets, threads and even some functions.

### Server sending side (server.py) :
1. Add a cloud server ip and port for the new camera stream in "cloud_server_sockets_ips" array.
2. Add the local cam stream url to the "local_cam_urls" array.
3. Add a new PUSH socket and connect this socket to the right cloud server socket ip
4. Capture the video stream of the camera with cam url
5. Create a new thread running "capture_send_video" function with:
          - The associated socket
         - The assiciated video capture
         - The numero of the camera for the creation of the topic
6. Start the created thread
7. Join the created thread for terminate
8. Release the video capture of the camera
9. Close the associated socket

### Client receiving side (app.py) :
1. First add the camera to the sending server by following the instructions
2. Add the camera into "cameras" array with:
           - Name of the camera you want to appear on the pages
           - Status of the camera: "active" or "inactive"
           - Name of the associated video_feed function.
                   For example for the 4th camera : {'name':'XXX view', 'status':'inactive','src':'video_feed_4'}
3. Add a new local port for receiving new cam data from the server into "local_sockets_ip" array.
4. Add a new PULL socket and bind it to the right local listening port
5. Add a new "last_visualization_time" variable for new thread to create
6. Create a new "video_feed" function similar to the others and in "make_response" add into the "receive_encode_video" function :
           - The socket you created
           - The last visualization time variable you created
7. Create a new thread running "receive_encode_video" function with:
           - The socket you created
           - The last visualization time variable you created
8. Start the created thread
