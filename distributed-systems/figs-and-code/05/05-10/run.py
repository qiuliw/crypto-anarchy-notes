import multiprocessing
import channel
import process
from time import sleep

def proc(chanID, procID, procIDSet):
	p = process.Process(chanID, procID, procIDSet)
	sleep(1)
	p.run()

if __name__ == "__main__":
	chanID = 1
	chan   = channel.Channel(chanID, True)

	procIDSet = [i for i in range(15)]

	procSet = (multiprocessing.Process(target=proc,args=(chanID,i,procIDSet,)) for i in procIDSet)

	for p in procSet:
		p.start()

	for p in procSet:
		p.join()
	
