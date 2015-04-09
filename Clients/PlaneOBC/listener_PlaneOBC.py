
import MissionDirector
import json

#-----------------------------------------------------------
# todo: handle messages from PlaneOBC
#
def callback(data):
	print "received message from PlaneOBC: \"" + str(data) + "\""
	print "todo: handle messages from PlaneOBC"
	json_data = json.loads(data)

	command = json_data["command"]
	json_data = json_data["send"]

	if command == "save_credentials":
		username = json_data["username"]
		password = json_data["password"]

		#save username and password in file

		# call Heimdall function to get highest image
		msg = {}
		msg["command"] = "get_top_filename"
		send_message_to_client(json.dumps(msg),ports.outport_Heimdall)






