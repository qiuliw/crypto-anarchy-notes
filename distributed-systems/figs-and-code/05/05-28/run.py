import multiprocessing
import channel
import process
import random
from constGrid import *
from time import sleep

def proc(chanID, x, y):
	p = process.Process(chanID, x,y)
	sleep(30)
	p.maintainOverlay()

if __name__ == "__main__":
	chanID = 1
	chan   = channel.Channel(chanID, True)

	f = open("t.txt","w")
	f.write('')
	f.close()

	f = open("b.txt","w")
	f.write('')
	f.close()
	
	numOfProcs = HEIGHT * WIDTH
	
	procIDSet = [(i*HEIGHT + j, i, j) for i in range(WIDTH) for j in range(HEIGHT)] 

	processes = set()
	for i in range(WIDTH):
		for j in range(HEIGHT):
			processes.add(multiprocessing.Process(target=proc,args=(chanID,i,j,)))
	
	for p in processes:
		p.start()

	for p in processes:
		p.join()
