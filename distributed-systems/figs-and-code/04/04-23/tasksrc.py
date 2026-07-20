import multiprocessing
import zmq, time, pickle, sys, random
from constPipe import * #-

def producer():
	context = zmq.Context()              
	socket  = context.socket(zmq.PUSH)        # create a push socket
	socket.bind("tcp://localhost:12345")                             # bind socket to address
	
	for i in range(100):                  # generate 100 workloads
		workload = random.randint(1, 100)   # compute workload
		socket.send(pickle.dumps(workload)) # send workload to worker

def worker():
	context = zmq.Context()
	socket  = context.socket(zmq.PULL)     # create a pull socket
	socket.connect("tcp://localhost:12345")                     # connect to task source 1

	while True:
		work = pickle.loads(socket.recv())   # receive work from a source
		print("Received " + str(work))
		time.sleep(work*0.01)        # pretend to work
