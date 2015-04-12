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
	print "usage:  [client-port]  [value-to-send]  [ip]"
	sys.exit(0)

ipaddr = "localhost"
if len(sys.argv) > 3:
	ipaddr = str(sys.argv[3])
	print("ipaddr == "+ipaddr)

#------------------------------------------------------
# Connect to server and send message
#
conntoserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conntoserver.connect((ipaddr, port))
conntoserver.send(msg)
conntoserver.close()

