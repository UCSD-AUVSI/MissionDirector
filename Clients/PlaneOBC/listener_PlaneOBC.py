
import MissionDirector
from Networking.send_message_to_client import send_message_to_client
from Networking import ports
import json
import time

#-----------------------------------------------------------
# todo: handle messages from PlaneOBC
#
def callback(data):
	json_data = json.loads(data)
	command = json_data["command"]

	print "\nreceived "+command +" message from PlaneOBC"
	print json_data


	if command == "save_credentials":
		time.sleep(10)

		username = json_data["username"]
		password = json_data["password"]

		#save username and password in file

		# call Heimdall function to get highest image
		msg = {}
		msg["command"] = "get_top_filename"

		send_message_to_client(json.dumps(msg),ports.outport_Heimdall)
		print "forwarded message from MissionDirector to Heimdall"

	elif command == "uploaded_image":
		print "Done, Image was uploaded"







