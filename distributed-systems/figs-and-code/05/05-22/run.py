import multiprocessing
import channel
import process
import random
from time import sleep

def proc(chanID, procID, procIDSet, initTX):
	p = process.Process(chanID, procID, procIDSet, initTX)
	sleep(1)
	if procID == 1:
		p.runElection()
	p.receive()
	
if __name__ == "__main__":
	chanID = 1
	chan   = channel.Channel(chanID, True)

	numOfProcs = 5
	
	procIDSet = [i for i in range(numOfProcs)]

	initTXSet = []

	for i in range(int(numOfProcs/2)):
		initTXSet.append(1)

	for i in range(int(numOfProcs/2)):
		initTXSet.append(2)

	initTXSet.append(2)
	random.shuffle(initTXSet)
	print(initTXSet)
	
	procSet = (multiprocessing.Process(target=proc,args=(chanID,i,procIDSet,initTXSet[i],)) for i in procIDSet)

	for p in procSet:
		p.start()

	for p in procSet:
		p.join()
