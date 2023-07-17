import zmq
import random

context = zmq.Context()

# Socket with direct access to the sink: used to syncronize start of batch
sink = context.socket(zmq.PUSH)
sink.connect("tcp://10.0.0.103:5558")

# Initialize random number generator
random.seed()

while True:
    workload = random.randint(1, 100)
    sink.send(b"ok")