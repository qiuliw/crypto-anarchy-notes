selectPeer(&Q); 
selectToSend(&bufs);
sendTo(Q, bufs); 

receiveFrom(Q, &bufr);
selectToKeep(p_view, bufr); 
