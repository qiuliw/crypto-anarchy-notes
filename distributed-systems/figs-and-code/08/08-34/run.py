import multiprocessing
from time import sleep
import channel
import coordinator
import participant

def coord(chanID, coordID, partIDSet):
	c = coordinator.Coordinator(chanID, coordID, partIDSet)
	sleep(5)
	c.run()

def part(chanID, coordID, partID, partIDSet):
	p = participant.Participant(chanID, coordID, partID, partIDSet)
	sleep(1)
	p.run()

if __name__ == "__main__":

	chanID		= 1
	coordID		= 2
	numOfPart = 9

	partIDSet = [i for i in range(coordID+1,coordID+numOfPart+1)]

	chan = channel.Channel(chanID, True)

	processes = set()
	processes.add(multiprocessing.Process(target=coord, args=(chanID, coordID, partIDSet,)))

	for p in partIDSet:
		processes.add(multiprocessing.Process(target=part, args=(chanID, coordID, p, partIDSet,))) 

	
	for p in processes:
		p.start()

	for p in processes:
		p.join()
