#-----------------------------------------------------------------
# Listens for messages from a human operator (i.e. manual inputs/overrides)
#

import MissionDirector
from Networking.send_message_to_client import send_message_to_client
from Networking import ports


#-----------------------------------------------------------------------------
# Callback to process an incoming message or command from the human operator
#
def callback(data):
	print "received message from human operator: \"" + str(data) + "\""
	datastr = str(data)
	
	#--------------------------------------------------------------------------
	# If message starts with "mavproxy:", forward to MAVProxy
	#
	if len(datastr) > 10 and datastr[:9] == "mavproxy:":
		send_message_to_client(datastr[9:], ports.outport_MAVProxy)
		print "forwarded message from HumanOperator to MAVProxy mdlink"
	
	#--------------------------------------------------------------------------
	# If message starts with "heimdall:", forward to Heimdall
	#
	if len(datastr) > 10 and datastr[:9] == "heimdall:":
		send_message_to_client(datastr[9:], ports.outport_Heimdall)
		print "forwarded message from HumanOperator to Heimdall"
	
	#--------------------------------------------------------------------------
	# If message starts with "planeobc:", forward to PlaneOBC
	#
	if len(datastr) > 10 and datastr[:9] == "planeobc:":
		send_message_to_client(datastr[9:], ports.outport_PlaneOBC)
		print "forwarded message from HumanOperator to PlaneOBC"
	
	#--------------------------------------------------------------------------
	# Todo: other types of messages/commands that a human operator might want to send
	
	


