class Process:
  def __init__(self, chanID, procID, procIDSet):                   
    self.chan.join(procID)
    self.procID     = int(procID)
    self.otherProcs.remove(self.procID)
    self.queue      = []                      # The request queue
    self.clock      = 0                       # The current logical clock

  def requestToEnter(self):                                         
    self.clock = self.clock + 1                         # Increment clock value
    self.queue.append((self.clock, self.procID, ENTER)) # Append request to q
    self.cleanupQ()                                     # Sort the queue
    self.chan.sendTo(self.otherProcs, (self.clock, self.procID, ENTER)) # Send request

  def ackToEnter(self, requester):
    self.clock = self.clock + 1                         # Increment clock value
    self.chan.sendTo(requester, (self.clock, self.procID, ACK)) # Permit other

  def release(self):
    tmp = [r for r in self.queue[1:] if r[2] == ENTER]  # Remove all ACKs
    self.queue = tmp                                    # and copy to new queue
    self.clock = self.clock + 1                         # Increment clock value
    self.chan.sendTo(self.otherProcs, (self.clock, self.procID, RELEASE)) # Release
    
  def allowedToEnter(self):
    commProcs = set([req[1] for req in self.queue[1:]]) # See who has sent a message
    return (self.queue[0][1] == self.procID and len(self.otherProcs) == len(commProcs))
