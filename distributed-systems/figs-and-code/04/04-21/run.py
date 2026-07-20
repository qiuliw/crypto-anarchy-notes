import multiprocessing #-
import zmq
from time import sleep #-

def server():
  context = zmq.Context()
  socket  = context.socket(zmq.REP)       # create reply socket
  socket.bind("tcp://*:12345")            # bind socket to address

  while True:
    message = socket.recv()               # wait for incoming message
    if not "STOP" in str(message):        # if not to stop...
      reply = str(message.decode())+'*'   # append "*" to message
      socket.send(reply.encode())         # send it away (encoded)
    else:                         
      break                               # break out of loop and end

def client():
  context = zmq.Context()
  socket  = context.socket(zmq.REQ)       # create request socket

  socket.connect("tcp://localhost:12345") # block until connected
  socket.send(b"Hello world")             # send message
  message = socket.recv()                 # block until response
  socket.send(b"STOP")                    # tell server to stop
  print(message.decode())                 # print result
#-
if __name__ == "__main__": #-
  s = multiprocessing.Process(target=server) #-
  c = multiprocessing.Process(target=client) #-
#-
  s.start() #-
  sleep(2) #-
  c.start() #-
  c.join() #-
  s.join() #-
