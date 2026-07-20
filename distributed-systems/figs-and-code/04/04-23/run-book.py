def producer():
  context = zmq.Context()              
  socket  = context.socket(zmq.PUSH)      # create a push socket
  socket.bind("tcp://127.0.0.1:12345")    # bind socket to address
  
  while True:
    workload = random.randint(1, 100)     # compute workload
    socket.send(pickle.dumps(workload))   # send workload to worker
    time.sleep(workload/NWORKERS)         # balance production by waiting 

def worker(id):
  context = zmq.Context()
  socket  = context.socket(zmq.PULL)      # create a pull socket
  socket.connect("tcp://localhost:12345") # connect to the producer

  while True:
    work = pickle.loads(socket.recv())     # receive work from a source
    time.sleep(work)                       # pretend to work
    
