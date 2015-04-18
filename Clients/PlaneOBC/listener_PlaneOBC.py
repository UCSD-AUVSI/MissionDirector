
import MissionDirector
from Networking.send_message_to_client import send_message_to_client
from Networking import ports
import json
import time

#-----------------------------------------------------------
# todo: handle messages from PlaneOBC
#
def callback(data):

	print "received message from PlaneOBC: \"" + str(data) + "\""
	
	# this needs to be a common interface between all UCSD AUVSI software parts: MissionDirector, Heimdall, NewOnboardSuite, etc.
	json_data = json.loads(data)
	command = json_data["command"]
	args = json_data["args"]
	
	if command == "save_credentials":
		username = args["username"]
		password = args["password"]
		
		#save username and password in file
		
		# call Heimdall function to get highest image
		msg = {}
		msg["command"] = "get_top_filename"

		send_message_to_client(json.dumps(msg),ports.outport_Heimdall)
		print "forwarded message from MissionDirector to Heimdall"

	elif command == "uploaded_image":
		print "Done, Image was uploaded"







