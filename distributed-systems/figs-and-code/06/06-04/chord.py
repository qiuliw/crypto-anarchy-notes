import channel #-
import random, math #-
from constChord import * #-
#-
class ChordNode:
#-
  def __init__(self, channelID, nodeID, nodeSet, nBits): #- 
    self.channel = channel.Channel(channelID)            # Create ref to actual channel #-
    self.channel.join(nodeID)                            #-
#-
    self.nBits   = nBits                                 # Num of bits for the ID space #-
    self.nodeSet = nodeSet                               # Participating Chord nodes     #-
    self.MAXPROC = pow(2,nBits)                          # Maximum num of processes    #-
    self.nodeID  = int(nodeID)                           # This node #-
    self.nodeInd = self.nodeSet.index(nodeID)            # Position of this node in the Chord ring #-
    self.FT      = [None for i in range(self.nBits+2)]   # FT[0] is predecessor, FT[nBits+2] is this node #-
#-
  def __inbetween(self, key, lwb, upb):                                         #-
    if lwb <= upb:                                                            #-
      result = (lwb <= key and key < upb)                                         #-
    else:                                                                     #- 
      result = ((lwb <= key and key < upb + self.MAXPROC) or (lwb <= key + self.MAXPROC and key < upb)) #-
    return result #-

  def __succNode(self, key):
    if (key <= self.nodeSet[0] or
        key > self.nodeSet[len(self.nodeSet)-1]): # key is in segment for which
      return self.nodeSet[0]                      # this node is responsible
    for i in range(1,len(self.nodeSet)):
      if (key <= self.nodeSet[i]):                # key is in segment for which 
        return self.nodeSet[i]                    # node (i+1) may be responsible
    
  def __finger(self, i):
    return self.__succNode((self.nodeID + pow(2,i-1)) % self.MAXPROC) # succ(p+2^(i-1))

  def __recomputeFingerTable(self): 
    self.FT[0]  = self.nodeSet[(self.nodeInd - 1)%len(self.nodeSet)] # Predecessor 
    self.FT[1:] = [self.__finger(i) for i in range(1,self.nBits+1)]  # Successors 
    self.FT.append(self.nodeID)                                      # This node 

  def __localSuccNode(self, key):
    if self.__inbetween(key, self.FT[0]+1, self.nodeID+1):   # key in (pred,self]
      return self.nodeID                                     # this node is responsible
    elif self.__inbetween(key, self.nodeID+1, self.FT[1]):   # key in (self,FT[1]]
      return self.FT[1]                                      # successor responsible
    for i in range(1, self.nBits+2):                         # go through rest of FT
      if self.__inbetween(key, self.FT[i], self.FT[(i+1)]):  # key in [FT[i],FT[i+1])
        return self.FT[i]                                    # FT[i] is responsible
#- 
  def run(self): #-
    self.__recomputeFingerTable() #-
    print(">>>",self.nodeID,": ",self.FT) #-
#-
    while True: #-
      message = self.channel.recvFromAny()                   # Wait for any request #-
      sender  = message[0]                                   # Identify the sender #-
      request = message[1]                                   # And the actual request #-
      if request[0] == STOP: #-
        break #-
      if request[0] == LOOKUP_REQ:                           # A lookup request #-
        nextID = self.__localSuccNode(request[1])            # look up next node #-
        self.channel.sendTo(sender, (LOOKUP_REP, nextID)) # return to sender #-
    return #-
#-
class ChordClient: #-
  def __init__(self, channelID, nodeID, nodeSet, nBits):                 #-
    self.channel = channel.Channel(channelID) #-
    self.channel.join(nodeID) #-
#-
    self.nodeID  = nodeID #-
    self.nodeSet = nodeSet #-
    self.nBits   = nBits #-
#-
  def run(self, numberOfRuns): #-
    procs = self.nodeSet #-
    procs.sort() #-
#-
    for k in range(numberOfRuns): #-
      p   = 28 # procs[random.randint(0,len(procs)-1)] #-
      key = 12 # random.randint(0,pow(2,self.nBits)) #-
      route = [p] #-
#-
      self.channel.sendTo(p, (LOOKUP_REQ, key) ) #-
      msg = self.channel.recvFromAny() #-
#-      
      route.append(msg[1][1]) #-
#-
      while msg[1][1] != p: #-
        p = msg[1][1] #-
        self.channel.sendTo(p,(LOOKUP_REQ, key)) #-
        msg = self.channel.recvFrom(p) #-
        route.append(msg[1][1]) #-
      print(self.nodeID, "Client got answer for", key, "from", p, "through route", route) #-
#-
    self.channel.sendTo(procs, (STOP)) #-
