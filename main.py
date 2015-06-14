import sys
from Networking import server_multiport
from Networking import ports
from Clients.Heimdall import listener_Heimdall
from Clients.MAVProxyC import listener_MAVProxy
from Clients.HumanOperator import listener_HumanOperator
from Clients.PlaneOBC import listener_PlaneOBC
from interoperability import globalvar_connection_interop as InterOP


#-----------------------------------------------------------
# main(): setup and start server
#
def main(argv):

	if len(argv) < 1:
		print("usage:  {ip-address-for-listen}  {optional:use-insecure-comms?}")
		quit()

	#start interop connection
	InterOP.connection.threadedconnect()
	#start the sending of data
	InterOP.connection.start_interop()

	sslcertsfolder = "/home/auvsi/AUVSI/sslcerts/"
	ports.PlaneOBC_listeningssldetails = server_multiport.SSLSecurityDetails(True)
	ports.PlaneOBC_listeningssldetails.cacerts = sslcertsfolder+"nobs-auvsi-cert-server.crt"
	ports.PlaneOBC_listeningssldetails.certfile = sslcertsfolder+"MDclientJason.crt"
	ports.PlaneOBC_listeningssldetails.keyfile = sslcertsfolder+"MDclientJason.key.nopass"

	# Setup several parallel listeners
	ports_and_callbacks = []
	ports_and_callbacks.append((ports.listenport_MAVProxy, listener_MAVProxy.callback, server_multiport.SSLSecurityDetails(False)))
	ports_and_callbacks.append((ports.listenport_Heimdall, listener_Heimdall.callback, server_multiport.SSLSecurityDetails(False)))
	ports_and_callbacks.append((ports.listenport_HumanOperator, listener_HumanOperator.callback, server_multiport.SSLSecurityDetails(False)))
	if len(argv) > 1:
		try:
			if int(argv[1]) != 0:
				ports.PlaneOBC_use_secure_comms_boolean = False
				ports.PlaneOBC_listeningssldetails = server_multiport.SSLSecurityDetails(False)
				print("using UNSECURE comms with PlaneOBC !!")
			else:
				print("using secure comms with PlaneOBC")
		except:
			print("something happened, when asking for insecure comms just use an integer 0 or 1")
	ports_and_callbacks.append((ports.listenport_PlaneOBC, listener_PlaneOBC.callback, ports.PlaneOBC_listeningssldetails))

	# Start server and wait here for keyboard interrupt, and keep trying to start connections
	s = server_multiport.server()
	s.start(ports_and_callbacks, argv[0], True, True)


#-----------------------------------------------------------
# execute main()... this needs to be at the end
#
if __name__ == "__main__":
	main(sys.argv[1:])
