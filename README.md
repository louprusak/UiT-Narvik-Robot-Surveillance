# UiT-Narvik-Robot-Surveillance
---
Web based view for lab's robot surveillance cameras.

*Uses a server to video capture the camera streams and send it in broadcast using ZMQ.*
*The flask web app gets this streams from the server and display it in different ways.*

*Need to configure sockets option and bindings for sending and receiving.*

**Made with Python 3.8**

---
## Python packages to install before : 
- Flask 2.3.2 : `pip install flask`
- Flask-WTF 1.1.1 : `pip install flask-wtf`
- OpenCv 2 : `pip install opencv-python`
- ZMQ 25.1.0 : `pip install pyzmq`

---
## Modify the urls and sockets : 
You need to modify the cameras urls and data and also the sockets urls and options to fit to your network setup.

### Modify server configuration :
1. Modify cameras url in the "cam_urls" array.
2. Modify the sockets bind url for each sockets. Don't forget to keep different ports.

### Modify client (web app) configuration : 
1. Modify cameras url in the "cam_urls" array.
2. Change sockets binding ips to correspondant server socket emmiting ip adress.

---
## Add other cameras or streams : 
if you want to add or remove some cameras or streams, you need to modify server and client configuration.
You need to add ip adresses, cameras data, sockets, threads and even some functions.
