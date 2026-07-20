import channel
import random
from time import sleep
from constGrid import *
import os

VIEWSIZE	 = 10
SWAPSIZE	 = 5
SwapReqApp = 1000
SwapResApp = 2000
SwapReqPSS = 3000
SwapResPSS = 4000

SwapIgnoreApp = 5000
SwapIgnorePSS = 6000
ID				 = 0
COL				 = 1
ROW				 = 2
AGE				 = 3

class Process:

	def __id(self,i,j): # Assign a nonzero identifier to each point of the grid
		return i*HEIGHT + j + 1

	def __distance(self, p, q): # Computes the Manhattan distance between two nodes
		dx = min(abs(p[COL] - q[COL]), WIDTH - abs(p[COL] - q[COL]))
		dy = min(abs(p[ROW] - q[ROW]), WIDTH - abs(p[ROW] - q[ROW]))
		return (dx, dy, dx + dy)

	def __init__(self, chanID, col, row):
		self.procID		 = self.__id(col,row)

		self.chan		   = channel.Channel(chanID) 
		self.chan.join(self.procID)						

		self.node			 = (self.procID, col, row, 0)	 # For all nodes, we also keep col and row
		self.procGrid	 = [(self.__id(i,j),i,j, 0) for i in range(WIDTH) for j in range(HEIGHT)]
		self.others		 = self.procGrid.copy()				# Construct a view of all other nodes
		self.others.remove(self.node)								# in the network (excl. yourself)
		self.neighbor	 = [random.choice(self.others) for i in range(4)] # Your neighbors
		self.viewPSS	 = random.sample(self.others, k = VIEWSIZE)				# Initial PSS view
		self.viewApp	 = random.sample(self.others, k = VIEWSIZE)				# Initial APP view

	def __selectOldestNeighbor(self, view):
		ageView = [(e[AGE], e[ID], e[COL], e[ROW]) for e in view]
		ageView.sort()
		oldestAge = ageView[-1][0]
		oldies = [p for p in ageView if p[0] == oldestAge]
		p = random.choice(oldies)
		return (p[1],p[2],p[3],p[0])

	def __incrAge(self, view):
		return list([(v[0], v[1], v[2], v[3] + 1) for v in view])

	def __zeroAge(self, view):
		return list([(v[0], v[1], v[2], 0) for v in view])

	def __removeDuplicates(self, view): # Keeps the oldest entries
		returnView = []
		for p in view:
			plist = [(q[AGE],q[ID],q[COL],q[ROW]) for q in view if q[ID] == p[ID]]
			plist.sort()
			q = plist[-1]
			returnView.append((q[1],q[2],q[3],q[0]))
		return returnView

	def __ismember(self,view,node):
		return node[ID] in [v[ID] for v in view]

	def __viewDifference(self, view1, view2): # remove elements from view1 that are in view2
		return list([v1 for v1 in view1 if v1[ID] not in [v2[ID] for v2 in view2]])

	def __selectFromView(self, q, view, total):
		# Compute the topology-optimal view by keeping the nodes closest to q
		distances = [(self.__distance(p,q)[2],p) for p in view]
		distances.sort()
		newView = [distances[i][1] for i in range(len(distances))]
		newView = self.__removeDuplicates(newView)
		return list([newView[i] for i in range(min(len(newView),total))])

	def __maintainViews(self, probSwapApp, probSwapPSS): 
		# Called regularly to mimick the behavior of separate threads each maintaining
		# their own view. The parameter 'probSwapX' gives the probability (in
		# terms of a percentage) that the process will actually initiate an exchange.
		selectedPeerApp = (0,0,0) # There is no node that has this identity and
		selectedPeerPSS = (0,0,0) # is used to also check if an exchange was initiated. 

		if random.randint(1,100) <= probSwapApp:
			# Time to initiate an application-level exchange
			selectedPeerApp = self.__selectOldestNeighbor(self.viewApp)
			assert selectedPeerApp[0] != self.node[0] # Critical to avoid blocking
			self.viewApp.remove(selectedPeerApp)
			swapViewSendApp = self.viewApp.copy()
			swapViewSendApp.extend(self.viewPSS)			# Add ramdomness from the PSS view
			swapViewSendApp.append(self.node)					# Add yourself to the exchange
			
			# At this point, select the best nodes from the view so far to hand over
			# to the selected peer, and pass these on.
			swapViewSendApp = self.__selectFromView(selectedPeerApp, swapViewSendApp, SWAPSIZE)
			self.chan.sendTo(selectedPeerApp[0], (SwapReqApp, self.node, swapViewSendApp))
			self.viewApp = self.__incrAge(self.viewApp)
			
		if random.randint(1,100) <= probSwapPSS:
			# Time to initiate a peer-sampling exchange to mimick randomly selecting peers
			self.viewPSS = self.__incrAge(self.viewPSS)
			selectedPeerPSS = self.__selectOldestNeighbor(self.viewPSS)
			assert selectedPeerPSS[0] != self.node[0] # Critical to avoid blocking
			self.viewPSS.remove(selectedPeerPSS)

			swapViewSendPSS = self.viewPSS.copy()
			# Reinsert the selectedPeer, but as a fresh peer to give precedence to others
			reinsertPeer = (selectedPeerPSS[ID],selectedPeerPSS[COL],selectedPeerPSS[ROW],0)
			self.viewPSS.append(reinsertPeer)

			# Randomly select other peers, keeping in mind that this process will include
			# itself in that selection
			swapViewSendPSS = random.sample(swapViewSendPSS, k = SWAPSIZE-1) 
			swapViewSendPSS.append(self.node) 
			self.chan.sendTo(selectedPeerPSS[0], (SwapReqPSS, self.node, swapViewSendPSS))
			
		while True: # Just continue until there are no more messages to process
			# If an exchange has been initiated, be sure to block until you get a
			# response. This node initiated an exchange only if selectedPeer has been
			# identified from the cache. Otherwise, check if there are any pending
			# messages and if not, return. Note that because messages are sent
			# asynchronously, and we check for any incoming message, we have effectively
			# prevented deadlocks caused by processes waiting for replies.

			block = (selectedPeerApp != (0,0,0)) or (selectedPeerPSS != (0,0,0))
			msg = self.chan.recvFromAny(block)
			if msg == None:
				# This process was just helping out. No work to do so simply bail out.
				return

			# At this point, the node has received a message: either a response to the
			# previously initiated exchange, or concurrent requests for an exchange.
			sender = msg[0]
			msgtype, msgsend, msgdata = msg[1][0], msg[1][1], msg[1][2]
			if msgtype == SwapResApp:
				# If the incoming message is the result of an initiated exchange, it must come
				# from the previously selected peer.
				assert sender == selectedPeerApp[0]
				swapViewRecvApp = self.viewApp.copy()          
				zeroViewPSS			= self.__zeroAge(self.viewPSS) 
				swapViewRecvApp.extend(zeroViewPSS)            # Add randomness from PSS
				self.viewApp = self.__selectFromView(self.node, swapViewRecvApp, VIEWSIZE)
				 
				swapViewRecvApp = self.__zeroAge(msgdata)			 # Get proposed data from selectedPeer
				swapViewRecvApp.extend(self.viewApp)           # Add what you already know and remove
				swapViewRecvApp = self.__viewDifference(swapViewRecvApp,[self.node]) # yourself

				# At this point we can construct a new viewAPP based on swapViewRecvApp.
				self.viewApp = self.__selectFromView(self.node, swapViewRecvApp, VIEWSIZE)

				assert not self.__ismember(self.viewApp, self.node) #-
				# This process is finished. By setting selectedPeerApp back to (0,0,0,0) it will
				# be able to process other messages (if any)
				selectedPeerApp = (0,0,0)
				continue

			elif msgtype == SwapReqApp:
				if selectedPeerApp != (0,0,0):
					# There was a concurrent exchange initiated with this node. Just drop this
					# request, but tell the other to drop out as well.
					self.chan.sendTo(sender, (SwapIgnoreApp, self.node, []))
					continue # You're still waiting for a response from the selected App peer 
				else:
					# A swap has been initiated, but not by this process.
					swapViewReplyApp = self.viewApp.copy() # Take what you already know
					swapViewReplyApp.extend(self.viewPSS)  # Add more stuff from PSS layer
					swapViewReplyApp.append(self.node)     # Add yourself

					# Remove what was sent to maximize diversity
					swapViewReplyApp = self.__viewDifference(swapViewReplyApp, msgdata) 

					# Construct a response that is optimal for the requester
					swapViewReplyApp = self.__selectFromView(self.procGrid[sender-1], swapViewReplyApp, SWAPSIZE)
					self.chan.sendTo(sender, (SwapResApp, self.node, swapViewReplyApp))

					# Adjust your own viewAPP 
					swapViewRecvApp = self.__zeroAge(msgdata) # Get the proposed data from selectedPeer
					swapViewRecvApp.extend(self.viewApp)      # Add what you already have, but not
					swapViewRecvApp = self.__viewDifference(swapViewRecvApp,[self.node]) # yourself

					# At this point we can construct a new viewAPP based on swapViewRecv.
					self.viewApp = self.__selectFromView(self.node, swapViewRecvApp, VIEWSIZE)

					assert not self.__ismember(self.viewApp, self.node) # Important to avoid blocking #-
					continue

			elif msgtype == SwapIgnoreApp:
				# The initiated exchange cannot be handled. Simply drop the whole attempt
				self.viewApp.append(selectedPeerApp) # append the selectedPeer again to the view
				selectedPeerApp = (0,0,0)
				continue
			
			elif msgtype == SwapResPSS:
				# We need to be sure that we construct a correct viewPSS. To that end, remove
				# anything what was sent from what you already know. Also remove any reference
				# to yourself (viewPSS is not supposed to refer to this node)
				swapViewRecvPSS = self.__viewDifference(msgdata, self.viewPSS)
				swapViewRecvPSS = self.__viewDifference(swapViewRecvPSS, [self.node])
				swapViewSendPSS = self.__viewDifference(swapViewSendPSS, [self.node])
				self.viewPSS = self.__viewDifference(self.viewPSS, swapViewSendPSS)

				# The PSS view has been sufficiently cleaned. Fill it with stuff that was
				# received, If there is room, reinsert the entries this process sent to the
				# selected peer
				while (len(self.viewPSS) < VIEWSIZE) and (len(swapViewRecvPSS) > 0):
					p = random.choice(swapViewRecvPSS)
					self.viewPSS.append(p)
					swapViewRecvPSS.remove(p)

				while (len(self.viewPSS) < VIEWSIZE) and (len(swapViewSendPSS) > 0) :
					p = random.choice(swapViewSendPSS)
					self.viewPSS.append(p)
					swapViewSendPSS.remove(p)

				assert not self.__ismember(self.viewPSS, self.node) # Important to avoid blocking #-

				# This process is done. See if there is other work to do.
				selectedPeerPSS = (0,0,0)
				continue
					
			elif msgtype == SwapReqPSS:
				if selectedPeerPSS != (0,0,0):
					# There was a concurrent exchange initiated with this node. Just drop this request.
					self.chan.sendTo(sender, (SwapIgnorePSS, self.node, []))
					continue
				else:
					swapViewReplyPSS = self.__viewDifference(msgdata, self.viewPSS)
					swapViewReplyPSS = self.__viewDifference(swapViewReplyPSS, [self.node])
					assert sender != self.node[0]
					self.chan.sendTo(sender, (SwapResPSS, self.node, swapViewReplyPSS))
					self.viewPSS = self.__viewDifference(self.viewPSS, swapViewReplyPSS)
					msgdata = self.__viewDifference(msgdata, [self.node])
					
					while (len(self.viewPSS) < VIEWSIZE) and (len(msgdata) > 0):
						p = random.choice(msgdata)
						self.viewPSS.append(p)
						msgdata.remove(p)
						
					assert not self.__ismember(self.viewPSS, self.node)
					selectedPeerPSS = (0,0,0)
					continue
					
			elif msgtype == SwapIgnorePSS:
				# The initiated exchange cannot be handled. Simply drop the whole attempt
				self.viewPSS.append(selectedPeerPSS)
				selectedPeerPSS = (0,0,0)
				continue

	def maintainOverlay(self):
		while True:
			sleep(1)
			self.__maintainViews(50, 50)
			for p in self.viewApp:
				for i in range(4):
					if self.__distance(self.neighbor[i],self.node)[2] > self.__distance(self.neighbor[i],p)[2]:
						self.neighbor[i] = p
			if [self.__distance(self.neighbor[i],self.node)[2] for i in range(4)] == [1,1,1,1]:
				# No more work to do, just help others
				f = open("t.txt", "a")
				f.write('%03d'%self.procID + "\n")
				f.close()
				os.system('wc t.txt')
				break

		while True:
			sleep(1)
			self.__maintainViews(0, 50)

