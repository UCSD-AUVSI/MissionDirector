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
	json_data = json.loads(data)
	redirect = json_data["redirect"]

	print "\nreceived "+redirect +" message from HumanOperator"
	print json_data

	#--------------------------------------------------------------------------
	# If message starts with "mavproxy:", forward to MAVProxy
	#
	if redirect == "mavproxy":
		send_message_to_client(json.dumps(json_data), ports.outport_MAVProxy)
		print "forwarded message from HumanOperator to MAVProxy mdlink"
	#--------------------------------------------------------------------------
	# If message starts with "heimdall:", forward to Heimdall
	#
	if redirect == "heimdall":
		send_message_to_client(json.dumps(json_data), ports.outport_Heimdall)
		print "forwarded message from HumanOperator to Heimdall"
	
	#--------------------------------------------------------------------------
	# If message starts with "planeobc:", forward to PlaneOBC
	#
	if redirect == "planeobc":
		json_data={}
		json_data["username"] = "test"
		json_data["password"] = "test"
		json_data["ip"] = "test"
		json_data["subnet"] = "test"
		json_data["folder"] = "test"
		json_data["command"] = "start"
		time.sleep(10)
		send_message_to_client(json.dumps(json_data), ports.outport_PlaneOBC)
		print "forwarded message from HumanOperator to PlaneOBC"
	
	#--------------------------------------------------------------------------
	# Todo: other types of messages/commands that a human operator might want to send
	
	


