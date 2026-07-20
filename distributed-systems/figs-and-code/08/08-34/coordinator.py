import channel, stablelog #-
from time import sleep    #-
from const2PC import *    #-
#-
class Coordinator:
  def __init__(self, chanID, coordID, partIDSet): #-
    self.chan         = channel.Channel(chanID) #-
    self.coordinator  = coordID #-
    self.chan.join(self.coordinator) #-
#-
    self.participants = partIDSet #-
    self.log          = stablelog.createLog(self.coordinator) #-
#-
  def run(self):
    self.log.info('INIT')             #-
    yetToReceive = list(self.participants)
    self.log.info('WAIT')
    self.chan.sendTo(self.participants, VOTE_REQUEST)
    while len(yetToReceive) > 0:
      msg = self.chan.recvFrom(self.participants, BLOCK, TIMEOUT)
      if msg == -1 or (msg[1] == VOTE_ABORT):
        self.log.info('ABORT')
        self.chan.sendTo(self.participants, GLOBAL_ABORT)
        return
      else: # msg[1] == VOTE_COMMIT
        yetToReceive.remove(msg[0])
    self.log.info('COMMIT')
    self.chan.sendTo(self.participants, GLOBAL_COMMIT)
