
import MissionDirector
from Networking.send_message_to_client import send_message_to_client
from Networking import ports
import json
import time

#-----------------------------------------------------------
# todo: handle messages from PlaneOBC
#
def callback(data, FromIPaddr):

	print "received message from PlaneOBC: \"" + str(data) + "\""
	
	# this needs to be a common interface between all UCSD AUVSI software parts: MissionDirector, Heimdall, NewOnboardSuite, etc.
	json_data = json.loads(data)
	cmd = json_data["cmd"]
	args = json_data["args"]
	
	if cmd == "status":
		print("PlaneOBC reported status: "+str(args))
		send_message_to_client(json.dumps({"cmd":"status","args":{"from":"PlaneOBC","message":json.dumps(args)}}), ports.outport_HumanOperator, ports.IPaddr_HumanOperator)
	
	if cmd == "save_credentials":
		username = args["username"]
		password = args["password"]
		
		#save username and password in file
		
		# call Heimdall function to get highest image
		msg = {}
		msg["cmd"] = "get_top_filename"

		send_message_to_client(json.dumps(msg), ports.outport_Heimdall, ports.IPaddr_Heimdall)
		print "forwarded message from MissionDirector to Heimdall"

	elif cmd == "uploaded_image":
		print "Done, Image was uploaded"







