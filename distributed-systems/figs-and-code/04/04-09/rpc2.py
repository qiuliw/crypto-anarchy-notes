import channel, pickle
from constRPC import * #-
                                                #-
class DBList:                                   #-
  def __init__(self, basicList):                #-
    self.value = list(basicList)                #-
                                                #-
  def append(self, data):                       #-
    self.value.extend(data) #-
    return self                                 #-

class Client: 
  def __init__(self, channelID, clientID, serverID):                           #-
    self.channel = channel.Channel(channelID) #-
    self.channel.join(clientID)     #-
    self.client  = clientID #-
    self.server  = serverID #-
                                                #-
  def append(self, data, dbList):
    assert isinstance(dbList, DBList)        #-
    msglst = (APPEND, data, dbList)             # message payload
    msgsnd = pickle.dumps(msglst)               # wrap call 
    self.channel.sendTo(self.server, msgsnd)    # send request to server 
    msgrcv = self.channel.recvFrom(self.server) # wait for response
    retval = pickle.loads(msgrcv[1])            # unwrap return value
    return retval                               # pass it to caller
#-
  def stop(self): #-
    msglst = (STOP,'','') #-
    msglst = pickle.dumps(msglst) #-
    self.channel.sendTo(self.server, msglst) #-
    return #-

class Server:
  def __init__(self, channelID, serverID):                           #-
    self.channel = channel.Channel(channelID) #-
    self.channel.join(serverID)     #-
    self.server  = serverID #-
#-
  def append(self, data, dbList):     #-         
    assert isinstance(dbList, DBList) #- Make sure we have a list
    return dbList.append(data)        #-
                                      #-
  def run(self):
    while True:
      msgreq = self.channel.recvFromAny() # wait for any request
      client = msgreq[0]                  # see who is the caller 
      msgrpc = pickle.loads(msgreq[1])    # unwrap the call
      if APPEND == msgrpc[0]:             # check what is being requested
        result = self.append(msgrpc[1], msgrpc[2]) # do local call 
        msgres = pickle.dumps(result)              # wrap the result
        self.channel.sendTo(client,msgres)         # send response
      elif STOP == msgrpc[0]: #- Time to stop
        return #-
      else:                                        #-
        pass # unsupported request, simply ignore  #-
      
      
    
