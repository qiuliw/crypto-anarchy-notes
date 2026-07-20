import multiprocessing
from time import sleep
import clientserver

def clientFunc(server):
	client = clientserver.Client()
	client.run()
	
def serverFunc():
	server = clientserver.Server()
	client = multiprocessing.Process(target=clientFunc,args=(server,))
	client.start()
	server.start()
	
if __name__ == "__main__":
	s = multiprocessing.Process(target=serverFunc)
	s.start()
	# Simply kill the server after a while
	sleep(10)
	s.terminate() 

