import multiprocessing #-
import zmq, time, pickle, sys, random #-
#-
NWORKERS = 10 #-
#-
def producer():
  context = zmq.Context()              
  socket  = context.socket(zmq.PUSH)      # create a push socket
  socket.bind("tcp://127.0.0.1:12345")    # bind socket to address
  
  while True:
    workload = random.randint(1, 100)     # compute workload
    print("Produced workload", format(workload,'03d')) #-
    socket.send(pickle.dumps(workload))   # send workload to worker
    time.sleep(workload/NWORKERS)         # balance production by waiting 

def worker(id):
  context = zmq.Context()
  socket  = context.socket(zmq.PULL)      # create a pull socket
  socket.connect("tcp://localhost:12345") # connect to the producer
  thisworker = format(id,'03d') #-

  while True:
    print("Worker " + thisworker + " wants work") #-    
    work = pickle.loads(socket.recv())     # receive work from a source
    print("Worker " + thisworker + " gets   " + format(work,'03d')) #-
    time.sleep(work)                       # pretend to work
    
if __name__ == "__main__": #-
  s = multiprocessing.Process(target=producer) #-
  w = [multiprocessing.Process(target=worker,args=(i+1,)) for i in range(NWORKERS)]#-
#-
  for i in range(NWORKERS): w[i].start() #-
  s.start() #-
  time.sleep(60) #-
  for i in range(NWORKERS): w[i].terminate() #-
  s.terminate() #-
