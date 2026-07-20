  def receive(self):
    msg = self.chan.recvFrom(self.otherProcs)[1]        # Pick up any message
    self.clock = max(self.clock, msg[0])                # Adjust clock value...
    self.clock = self.clock + 1                         # ...and increment
    if msg[2] == ENTER:                                
      self.queue.append(msg)                            # Append an ENTER request
      self.ackToEnter(msg[1])                           # and unconditionally allow
    elif msg[2] == ACK:                              
      self.queue.append(msg)                            # Append a received ACK
    elif msg[2] == RELEASE:
      del(self.queue[0])                                # Just remove first message
    self.cleanupQ()                                     # And sort and cleanup


