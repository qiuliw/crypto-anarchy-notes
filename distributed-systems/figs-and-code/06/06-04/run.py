import sys
import multiprocessing
from time import sleep
import channel
import chord
import random, math

def node(channelID, nodeID, nodeSet, nBits):
	chordNode = chord.ChordNode(channelID, nodeID, nodeSet, nBits)
	chordNode.run()
	
def client(channelID, clientID, nodeSet, nBits, numOfExp):
	clientNode = chord.ChordClient(channelID, clientID, nodeSet, nBits)
	sleep(5) # Reserve enough time to start the Chord network
	clientNode.run(numOfExp)

if __name__ == "__main__":
	m = int(sys.argv[1]) # number of bits
	n = int(sys.argv[2]) # number of Chord nodes
	r = int(sys.argv[3]) # number of experiments to run
	channelID = 1

	chan     = channel.Channel(channelID, True)
	nodeSet  = [1,4,9,11,14,18,20,21,28] 
#	nodeSet  = random.sample(range(pow(2,m)),n)
	nodeSet.sort()
	clientID = pow(2,m)

#	print(m, n, nodeSet, clientID)
	chordClient  =  multiprocessing.Process(target=client,args=(channelID,clientID,nodeSet,m,r,))
	chordNodeSet = [multiprocessing.Process(target=node,args=(channelID,i,nodeSet,m,)) for i in nodeSet]

	for chordNode in chordNodeSet:
		chordNode.start()

	chordClient.start()
	
	chordClient.join()
	for chordNode in chordNodeSet:
		chordNode.join()
