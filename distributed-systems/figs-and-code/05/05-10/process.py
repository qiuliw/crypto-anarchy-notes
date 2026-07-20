import channel #-
import random,time #-
from constCS import * #-
#-
class Process:
#-
  def __init__(self, chanID, procID, procIDSet):                   
    self.chan       = channel.Channel(chanID) # Create ref to actual channel #-
    self.chan.join(procID)
#-    
    self.procID     = int(procID)
    self.otherProcs = procIDSet               # Needed to multicast to others #-
    self.otherProcs.remove(self.procID)
    self.queue      = []                      # The request queue
    self.clock      = 0                       # The current logical clock

  def cleanupQ(self):                        #- 
    if len(self.queue) > 0:                  #-
      self.queue.sort()                      #- 
      # There should never be old ACK messages at the head of the queue   #-
      while self.queue[0][2] == ACK:         #-
        del(self.queue[0])                   #-
#-
  def requestToEnter(self):                                         
    self.clock = self.clock + 1                         # Increment clock value
    self.queue.append((self.clock, self.procID, ENTER)) # Append request to q
    self.cleanupQ()                                     # Sort the queue
    self.chan.sendTo(self.otherProcs, (self.clock, self.procID, ENTER)) # Send request

  def ackToEnter(self, requester):
    self.clock = self.clock + 1                         # Increment clock value
    self.chan.sendTo(requester, (self.clock, self.procID, ACK)) # Permit other

  def release(self):
    assert self.queue[0][1] == self.procID #-
    tmp = [r for r in self.queue[1:] if r[2] == ENTER]  # Remove all ACKs
    self.queue = tmp                                    # and copy to new queue
    self.clock = self.clock + 1                         # Increment clock value
    self.chan.sendTo(self.otherProcs, (self.clock, self.procID, RELEASE)) # Release
    
  def allowedToEnter(self):
    commProcs = set([req[1] for req in self.queue[1:]]) # See who has sent a message
    return (self.queue[0][1] == self.procID and len(self.otherProcs) == len(commProcs))

  def receive(self):
    msg = self.chan.recvFrom(self.otherProcs)[1]        # Pick up any message
    self.clock = max(self.clock, msg[0])                # Adjust clock value...
    self.clock = self.clock + 1                         # ...and increment
    if msg[2] == ENTER:                                
      self.queue.append(msg)                            # Append an ENTER request
      self.ackToEnter(msg[1])                         # and unconditionally allow
    elif msg[2] == ACK:                              
      self.queue.append(msg)                            # Append a received ACK
    elif msg[2] == RELEASE:
      assert self.queue[0][1] == msg[1] and self.queue[0][2] == ENTER #-
      del(self.queue[0])                                # Just remove first message
    self.cleanupQ()                                     # And sort and cleanup
#-
  def run(self): #-
    while True:                                  #- 
      if random.choice([True,False]):            #-
        self.requestToEnter()                    #-
        while not self.allowedToEnter():         #-
          self.receive()                         #-
        print(" IN:  ", str(self.procID).zfill(3),end=' ') #-
        time.sleep(random.randint(1,5))          #-
        print("-", str(self.procID).zfill(3))    #-
        self.release()                           #-
        continue                                 #-
      if random.choice([True,False]):            #-
        self.receive()                           #-
