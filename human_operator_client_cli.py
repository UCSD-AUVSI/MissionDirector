import socket, time, sys
import json
#------------------------------------------------------
# get arguments
#
try:
	port = int(sys.argv[1])
	# pass in json string
	msg =  sys.argv[2]
except:
	print "usage:  [client-port]  [value-to-send]"
	sys.exit(0)

#------------------------------------------------------
# Connect to server and send message
#
conntoserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conntoserver.connect(("localhost", port))
conntoserver.send(msg)
conntoserver.close()

