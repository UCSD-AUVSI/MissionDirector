#-----------------------------------------------------------------
# Listens for messages from a human operator (i.e. manual inputs/overrides)
#

import MissionDirector
from Networking.send_message_to_client import send_message_to_client
from Networking import ports
import json


#-----------------------------------------------------------------------------
# Callback to process an incoming message or command from the human operator
#
def callback(data):
	print "received message from human operator: \"" + str(data) + "\""
	
	# this needs to be a common interface between all UCSD AUVSI software parts: MissionDirector, Heimdall, NewOnboardSuite, etc.
	json_data = json.loads(data)
	command = json_data["command"]
	args = json_data["args"]
	
	#--------------------------------------------------------------------------
	# If command is "mavproxy:", forward argument "message" to MAVProxy
	#
	if command == "mavproxy:":
		msg = args["message"]
		send_message_to_client(msg, ports.outport_MAVProxy)
		print "forwarded message from HumanOperator to MAVProxy mdlink"
	
	#--------------------------------------------------------------------------
	# If command is "heimdall:", forward argument "message" to Heimdall
	#
	if command == "heimdall:":
		msg = args["message"]
		send_message_to_client(msg, ports.outport_Heimdall)
		print "forwarded message from HumanOperator to Heimdall"
	
	#--------------------------------------------------------------------------
	# If message starts with "planeobc:", forward argument "message" to PlaneOBC
	#
	if command == "planeobc:":
		msg = args["message"]
		ipaddr = args["ip"]
		send_message_to_client(msg, ports.outport_PlaneOBC, IPaddr=ipaddr)
		print "forwarded message from HumanOperator to PlaneOBC"
	
	#--------------------------------------------------------------------------
	# Todo: other types of messages/commands that a human operator might want to send
	
	


