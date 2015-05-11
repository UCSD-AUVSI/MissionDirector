#-----------------------------------------------------------------
# Listens for messages from a human operator (i.e. manual inputs/overrides)
#

import MissionDirector
from Networking.send_message_to_client import send_message_to_client
from Networking import ports
import json
import time


#-----------------------------------------------------------------------------
# Callback to process an incoming message or command from the human operator
#
def callback(data):
	print "received message from human operator: \"" + str(data) + "\""
	
	# this needs to be a common interface between all UCSD AUVSI software parts: MissionDirector, Heimdall, NewOnboardSuite, etc.
	json_data = json.loads(data)
	cmd = json_data["cmd"]
	args = json_data["args"]
	
	#--------------------------------------------------------------------------
	# If command is "mavproxy:", forward argument "message" to MAVProxy
	#
	if cmd == "mavproxy:":
		print("forwarding message from HumanOperator to MAVProxy mdlink")
		msg = args["message"]
		send_message_to_client(msg, ports.outport_MAVProxy)
	
	#--------------------------------------------------------------------------
	# If command is "heimdall:", forward argument "message" to Heimdall
	#
	if cmd == "heimdall:":
		print("forwarding message from HumanOperator to Heimdall")
		msg = args["message"]
		send_message_to_client(msg, ports.outport_Heimdall)
	
	#--------------------------------------------------------------------------
	# If message starts with "planeobc:", forward argument "message" to PlaneOBC
	#

	if cmd == "planeobc:":
		print("forwarding message from HumanOperator to PlaneOBC")
		msg = args["message"]
		ipaddr = args["ip"]
		send_message_to_client(msg, ports.outport_PlaneOBC, IPaddr=ipaddr)
	
	#--------------------------------------------------------------------------
	# Todo: other types of messages/commands that a human operator might want to send
	
	


