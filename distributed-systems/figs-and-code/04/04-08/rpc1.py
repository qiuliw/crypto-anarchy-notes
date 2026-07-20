import channel, pickle
from constRPC import * #-

class DBList:
  def __init__(self, basicList): #-
    self.value = list(basicList) #-
                                 #-
  def append(self, data):
    self.value.extend(data)
    return self

class Client: 
  def __init__(self, channelID, clientID, serverID):                            #-
    self.channel = channel.Channel(channelID) #-
    self.channel.join(clientID) #-
    self.client  = clientID #-
    self.server  = serverID #-
                                                #-
  def append(self, data, dbList):
    assert isinstance(dbList, DBList)        #-
    msglst = (APPEND, data, dbList)             # message payload
    self.channel.sendTo(self.server, msglst)    # send message to server 
    msgrcv = self.channel.recvFrom(self.server) # wait for an incoming message

    # A call to recvFrom returns a [senderID, message] pair
    return msgrcv[1]                            # pass returned message to caller
#-
  def stop(self): #-
    msglst = (STOP, '', '') #-
    self.channel.sendTo(self.server, msglst) #-
    return #-

class Server:
  def __init__(self, channelID, serverID):  #-
    self.channel = channel.Channel(channelID) #-
    self.channel.join(serverID) #-
    self.server  = serverID #-
#-
  def append(self, data, dbList):              
    assert isinstance(dbList, DBList) #- Make sure we have a list
    return dbList.append(data)

  def run(self):
    while True:
      msgreq = self.channel.recvFromAny() # wait for any request
      client = msgreq[0]                  # see who is the caller 
      msgrpc = msgreq[1]                  # fetch the actual request

      # At this point, msgreq should have the form (operation, data, list) 
      if APPEND == msgrpc[0]:          # check what is being requested
        result = self.append(msgrpc[1], msgrpc[2]) # do local call
        self.channel.sendTo(client,result)         # return response
      elif STOP == msgrpc[0]: #- Time to stop
        return #-
      else:  #-
        pass # unsupported request, simply ignore  #-
