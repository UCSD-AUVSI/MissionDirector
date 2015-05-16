import sys
from Networking import server_multiport
from Networking import ports
from Clients.Heimdall import listener_Heimdall
from Clients.MAVProxyC import listener_MAVProxy
from Clients.HumanOperator import listener_HumanOperator
from Clients.PlaneOBC import listener_PlaneOBC


#-----------------------------------------------------------
# main(): setup and start server
#
def main(argv):
	
	# Setup several parallel listeners
	ports_and_callbacks = []
	ports_and_callbacks.append((ports.listenport_MAVProxy, listener_MAVProxy.callback, False))
	ports_and_callbacks.append((ports.listenport_Heimdall, listener_Heimdall.callback, False))
	ports_and_callbacks.append((ports.hybridport_PlaneOBC, listener_PlaneOBC.callback, False))
	ports_and_callbacks.append((ports.listenport_HumanOperator, listener_HumanOperator.callback, False))
	
	# Start server and wait here for keyboard interrupt, and keep trying to start connections
	s = server_multiport.server()
	s.start(ports_and_callbacks, "localhost", True, True)


#-----------------------------------------------------------
# execute main()... this needs to be at the end
#
if __name__ == "__main__":
	main(sys.argv[1:])







