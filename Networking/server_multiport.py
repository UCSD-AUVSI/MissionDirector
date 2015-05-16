#-----------------------------------------------------------
# Multi-port parallel listen server; use start_server()
# Waits for keyboard interrupt
#

import select, socket, sys, time, threading
import ssl

class ThreadedListenSock:
	def __init__(self, mythread, myportnum):
		self.thread = mythread
		self.SocketBoundBoolean = False
		self.ClientConnectedOnSocket = False
		self.ClientSocket = ""
		self.portnum = myportnum

class SSLSecurityDetails:
	def __init__(self, boolarg):
		self.secured = boolarg
		self.certfile = ""
		self.keyfile = ""

#-------------------------------------------------------------------
# Starts a listen server, listening on as many ports as you provide
#
# Argument: a list of 3-tuples, each has: (port, callbackfunction, SSL-security)
#
# When messages are received on those ports, the callbacks are
#   called with the data that was provided in the message
#
class server:
	
	def __init__(self):
		self.keep_running = threading.Event()
		self.ThreadedListenSocks = []
		self.readytostart = True
	
	def stop(self):
		print "Beginning server shutdown..."
		self.keep_running.clear()
		for threadidx in range(len(self.ThreadedListenSocks)):
			self.ThreadedListenSocks[threadidx].thread.join()
		print "Server done shutting down."
		self.readytostart = True
	
	def CheckSocketOfClientOnPort(self, portnum):
		for idx in range(len(self.ThreadedListenSocks)):
			if self.ThreadedListenSocks[idx].portnum == portnum and self.ThreadedListenSocks[idx].ClientConnectedOnSocket:
				return True
		return False
	
	def CheckAllSocketsBound(self):
		socketsboundlen = len(self.ThreadedListenSocks)
		numsocketsbound = 0
		for idx in range(socketsboundlen):
			if self.ThreadedListenSocks[idx].SocketBoundBoolean:
				numsocketsbound = numsocketsbound + 1
		if numsocketsbound == socketsboundlen:
			return True
		return False
	
	def start(self, ports_and_callbacks, ipv4address, wait_for_interrupt, keep_retrying_to_bind_socket):
		
		if self.readytostart == True:
			self.readytostart = False
			
			# this will maintain an "on" state, that will shut down the threads when switched
			self.keep_running.set()
			
			self.ThreadedListenSocks = []
			SocketsBoundThreadIdx = 0
			for port_and_callback in ports_and_callbacks:
				self.ThreadedListenSocks.append(ThreadedListenSock(mythread=threading.Thread(target=self.start_port_listener, args=(port_and_callback[0], port_and_callback[1], ipv4address, port_and_callback[2], self.keep_running, keep_retrying_to_bind_socket, SocketsBoundThreadIdx)), myportnum=port_and_callback[0]))
				SocketsBoundThreadIdx = (SocketsBoundThreadIdx + 1)
			for threadidx in range(len(self.ThreadedListenSocks)):
				self.ThreadedListenSocks[threadidx].thread.daemon = True
				self.ThreadedListenSocks[threadidx].thread.start()
			
			if wait_for_interrupt:
				try:
					import ports
					needtoaddplaneobc = True
					while True:
						time.sleep(0.1)
						if self.CheckSocketOfClientOnPort(ports.hybridport_PlaneOBC) == False and needtoaddplaneobc == True:
							if ports.PlaneOBC_secure_socket_is_connected == True:
								needtoaddplaneobc = False
								print("STARTING PLANEOBC LISTENER~~~~~~")
								from Clients.PlaneOBC import listener_PlaneOBC
								SocketsBoundThreadIdx = len(self.ThreadedListenSocks)
								self.ThreadedListenSocks.append(ThreadedListenSock(mythread=threading.Thread(target=self.listen_on_given_socket, args=(ports.hybridport_PlaneOBC, listener_PlaneOBC.callback, ports.IPaddr_PlaneOBC, self.keep_running, SocketsBoundThreadIdx)), myportnum=ports.hybridport_PlaneOBC))
								self.ThreadedListenSocks[-1].thread.daemon = True
								self.ThreadedListenSocks[-1].thread.start()
				except KeyboardInterrupt:
					self.stop()
	
	#-----------------------------------------------------------
	def listen_on_given_socket(self, port, callback, ipv4address, keep_running_until_interrupt, thisthreadidx):
		
		import ports
		self.ThreadedListenSocks[thisthreadidx].SocketBoundBoolean = True
		self.ThreadedListenSocks[thisthreadidx].ClientConnectedOnSocket = True
		self.ThreadedListenSocks[thisthreadidx].ClientSocket = ports.PlaneOBC_secure_socket
		
		while keep_running_until_interrupt.is_set(): #keep receiving from this client until client shuts down
			#print "port "+str(port)+" is waiting for data from client..."
			data = self.ThreadedListenSocks[thisthreadidx].ClientSocket.recv(1024)
			if not data: continue
			#print "port "+str(port)+" received data from client: \"" + str(data) + "\""
			callback(data, (ipv4address, port))
		
		print("QUITTING PLANEOBC SSL SOCKET??????????????????????")
	
	#-----------------------------------------------------------
	# Listen on one port (don't use this outside this file)
	# When a message is received, give it to the callback
	# self is used to set ThreadedListenSocks
	#
	def start_port_listener(self, port, callback, ipv4address, ssl_security, keep_running_until_interrupt, keep_retrying_to_bind_socket, thisthreadidx):
	
		listensocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
		keeptrying = True
		while keeptrying == True:
			try:
				listensocket.bind((ipv4address, port))
				keeptrying = False
			except socket.error:
				print("server couldnt bind socket? "+str(sys.exc_info()[0]))
				if keep_retrying_to_bind_socket == False:
					print("failed to bind socket... quitting attempts")
					return
				time.sleep(0.5)
		
		listensocket.listen(0) # 0 for debugging; 3-5 for release version
		self.ThreadedListenSocks[thisthreadidx].SocketBoundBoolean = True
		print("socket successfully bound for listening at ip "+str(ipv4address)+" on port "+str(port))
		
		while keep_running_until_interrupt.is_set():
		
			rr,rw,err = select.select([listensocket],[],[],1)
			if rr:
				#print "port "+str(port)+" is waiting for a new client!"
				(clientsock, caddress) = listensocket.accept()
				
				if ssl_security.secured and ipv4address != "localhost":
					self.ThreadedListenSocks[thisthreadidx].ClientSocket = ssl.wrap_socket(clientsock, server_side=True, cerfile=ssl_security.certfile, keyfile=ssl_security.keyfile)
				else:
					self.ThreadedListenSocks[thisthreadidx].ClientSocket = clientsock
				self.ThreadedListenSocks[thisthreadidx].ClientConnectedOnSocket = True
				
				#print "port "+str(port)+" found a client at address: ", caddress
				
				while keep_running_until_interrupt.is_set(): #keep receiving from this client until client shuts down
					#print "port "+str(port)+" is waiting for data from client..."
					data = self.ThreadedListenSocks[thisthreadidx].ClientSocket.recv(1024)
					if not data: break
					#print "port "+str(port)+" received data from client: \"" + str(data) + "\""
					callback(data, caddress)
				
				self.ThreadedListenSocks[thisthreadidx].ClientSocket.close()
		
		listensocket.close()
		self.ThreadedListenSocks[thisthreadidx].SocketBoundBoolean = False
		print "Socket on port "+str(port)+" closed!"


