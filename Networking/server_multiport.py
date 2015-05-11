#-----------------------------------------------------------
# Multi-port parallel listen server; use start_server()
# Waits for keyboard interrupt
#

import select, socket, sys, time, threading
import ssl


#-------------------------------------------------------------------
# Starts a listen server, listening on as many ports as you provide
#
# Argument: a list of 3-tuples, each has: (port, callbackfunction, boolean-SSL-secured?)
#
# When messages are received on those ports, the callbacks are
#   called with the data that was provided in the message
#
class server:
	
	def __init__(self):
		self.keep_running = threading.Event()
		self.threads = []
		self.SocketsBoundBooleans = []
		self.readytostart = True
	
	def stop(self):
		print "Beginning server shutdown..."
		self.keep_running.clear()
		for thread in self.threads:
			thread.join()
		print "Server done shutting down."
		self.readytostart = True
	
	def CheckAllSocketsConnected(self):
		socketsboundlen = len(self.SocketsBoundBooleans)
		numsocketsbound = 0
		for idx in range(socketsboundlen):
			if self.SocketsBoundBooleans[idx]:
				numsocketsbound = numsocketsbound + 1
		if numsocketsbound == socketsboundlen:
			return True
		return False
	
	def start(self, ports_and_callbacks, ipv4address, wait_for_interrupt, keep_retrying_to_bind_socket):
		
		if self.readytostart == True:
			self.readytostart = False
			
			# this will maintain an "on" state, that will shut down the threads when switched
			self.keep_running.set()
			
			self.threads = []
			self.SocketsBoundBooleans = []
			SocketsBoundThreadIdx = 0
			for port_and_callback in ports_and_callbacks:
				self.threads.append(threading.Thread(target=self.start_port_listener, args=(port_and_callback[0], port_and_callback[1], ipv4address, port_and_callback[2], self.keep_running, keep_retrying_to_bind_socket, SocketsBoundThreadIdx)))
				self.SocketsBoundBooleans.append(False)
				SocketsBoundThreadIdx = (SocketsBoundThreadIdx + 1)
			for thread in self.threads:
				thread.daemon = True
				thread.start()
			
			if wait_for_interrupt:
				try:
					while True:
						time.sleep(0.1)
				except KeyboardInterrupt:
					self.stop()
	
	#-----------------------------------------------------------
	# Listen on one port (don't use this outside this file)
	# When a message is received, give it to the callback
	# self is used to set SocketsBoundBooleans
	#
	def start_port_listener(self, port, callback, ipv4address, ssl_secured, keep_running_until_interrupt, keep_retrying_to_bind_socket, thisthreadidx):
	
		if ssl_secured and ipv4address != "localhost":
			listensocket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			listensocket = ssl.wrap_socket(listensocket_,
							ssl_version=ssl.PROTOCOL_TLSv1,
							cert_reqs=ssl.CERT_REQUIRED,
							ca_certs='/etc/ssl/certs/ucsd-auvsi-cert.crt')
		else:
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
		self.SocketsBoundBooleans[thisthreadidx] = True
		print("socket successfully bound for listening at ip "+str(ipv4address)+" on port "+str(port))
	
		while keep_running_until_interrupt.is_set():
		
			rr,rw,err = select.select([listensocket],[],[],1)
			if rr:
				#print "port "+str(port)+" is waiting for a new client!"
				(clientsocket, caddress) = listensocket.accept()
				#print "port "+str(port)+" found a client at address: ", caddress
				
				while keep_running_until_interrupt.is_set(): #keep receiving from this client until client shuts down
					#print "port "+str(port)+" is waiting for data from client..."
					data = clientsocket.recv(1024)
					if not data: break
					#print "port "+str(port)+" received data from client: \"" + str(data) + "\""
					callback(data, caddress[0])
				
				clientsocket.close()
	
		listensocket.close()
		self.SocketsBoundBooleans[thisthreadidx] = False
		print "Socket on port "+str(port)+" closed!"


