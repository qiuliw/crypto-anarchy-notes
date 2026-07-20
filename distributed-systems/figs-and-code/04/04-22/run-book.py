import multiprocessing
import zmq, time

def server():
  context = zmq.Context()         
  socket = context.socket(zmq.PUB)          # create a publisher socket
  socket.bind("tcp://*:12345")              # bind socket to the address
  while True:                    
    time.sleep(5)                           # wait every 5 seconds
    t = "TIME " + time.asctime()
    socket.send(t.encode())                 # publish the current time

def client():
  context = zmq.Context()
  socket = context.socket(zmq.SUB)          # create a subscriber socket
  socket.connect("tcp://localhost:12345")   # connect to the server
  socket.setsockopt(zmq.SUBSCRIBE, b"TIME") # subscribe to TIME messages

  for i in range(5):      # Five iterations
    time = socket.recv()  # receive a message related to subscription 
    print(time.decode())  # print the result      
