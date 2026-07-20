import channel #-
import random  #-
#-
ELECTION = "1" #-
LEADER   = "2" #-
FOLLOWER = "3" #-
NOLEADER = "4" #-
STOP     = "5" #-
#-
class Process:
#-
  def __init__(self, chanID, procID, procIDSet, initTX):                   
    self.chan       = channel.Channel(chanID) # Create ref to actual channel #-
    self.chan.join(procID) #-
#-
    self.procID     = int(procID) #-
    self.otherProcs = procIDSet               # Needed to multicast to others #-
    self.otherProcs.remove(self.procID) #-
    self.otherProcs.sort() #-
#-    
    self.txID       = initTX       # Your own most recent transaction
    self.leader     = self.procID  # Who you believe may become leader
    self.lastTX     = self.txID    # What is the most recent transaction
    self.noleader   = False        # Are you still in the race for leader?

  def runElection(self): #-
#   print("Starting election", self.procID, self.txID) #-
    self.chan.sendTo(self.otherProcs, (ELECTION, self.leader, self.lastTX)) #-
#-
  def receive(self):
    followers = [] #-
#-    
    while True:
      msg             = self.chan.recvFrom(self.otherProcs)
      sender, payload = msg[0], msg[1]
#-      
      if payload[0] == ELECTION: # A process started an election
#       print("Received ELECTION", self.procID, self.leader, self.lastTX, payload) #-
        voteID, voteTX = payload[1], payload[2] 

        if self.lastTX < voteTX: # You're not up to date on most recent transaction
          self.leader = voteID   # Record the suspected leader
          self.lastTX = voteTX   # As well as the likely most recent transaction

        elif (self.lastTX == voteTX) and (self.leader < voteID): # Wrong leader
          self.leader = voteID   # Update your suspected leader

        elif (self.procID > voteID) and (self.txID >= voteTX) and (not self.noleader):
          # At this point, you may very well be the new leader (having a sufficiently
					# high process identifier as well as perhaps the most recent transaction).
					# No one has told you so far that you could not be leader. Tell the others.
          assert self.leader == self.procID #- 
          assert self.lastTX == self.txID   #-
#         print("Proc", self.procID, "believes it should be leader", self.leader, self.lastTX) #-
          self.chan.sendTo(self.otherProcs, (LEADER, self.procID, self.txID))

      if payload[0] == LEADER:
        # Check if the sender should indeed be leader
        if ((self.lastTX < payload[2]) or
            ((self.lastTX == payload[2]) and (self.leader <= payload[1]))):
          # The sender is more up-to-date than you, or is equally up-to-date but 
          # has a higher process identifier. Declare yourself follower.
#         print("Proc", self.procID, "believes leader is", payload[1]) #-
          self.chan.sendTo(sender, (FOLLOWER, self.procID))
        else:
          # Sender is wrong: you have information that the sender based its decision
          # on outdated information
#         print("Proc", self.procID, "tells no leader to", payload[1], "(", self.leader, ")", self.lastTX, "(", payload[2],")") #-
          self.chan.sendTo(sender, (NOLEADER))
#-
      if payload[0] == NOLEADER: #-
        # You are definitely out of the race. Make sure you stay out. #-
        self.noleader = True #-
#-
      if (payload[0] == FOLLOWER) and (not self.noleader): #-
        # You're still in the race. Record the follower and see if all other processes #-
        # are also now follower. That will tell you that have won the election.        #-
        followers.append(payload[1]) #-
        followers.sort() #-
        if followers == self.otherProcs: #-
          self.chan.sendTo(self.otherProcs, (STOP)) #-
          print("Leader is",self.procID,self.txID)  #-
          return #-
#-
      if payload[0] == STOP: #-
        return #-
