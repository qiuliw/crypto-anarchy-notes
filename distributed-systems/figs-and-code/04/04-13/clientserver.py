import rpyc
from constRPYC import * #-
from rpyc.utils.server import ForkingServer

class DBList(rpyc.Service):
	value = [] # Used to build a list of strings

	def exposed_append(self, data):
		self.value.extend(str(data)) # Extend the list with the data
		return self.value						 # Return the current list

	def exposed_value(self):
		return self.value

class Server:
	# Create a forking server at inititalization time and immediately start it.
	# For each incoming request, the server will spawn another process to handle
	# that request. The process that started the (main) server can simply kill
	# it when it's time to do so.
	def __init__(self):
		self.server = ForkingServer(DBList, hostname=SERVER, port=PORT)
		
	def start(self):
		self.server.start()

class Client:
	def run(self):
		conn = rpyc.connect(SERVER, PORT) # Connect to the server
		conn.root.exposed_append(2)				# Call an exposed operation,
		conn.root.exposed_append(4)				# and append two elements
		print(conn.root.exposed_value())	# Print the result
		
