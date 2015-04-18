
import MissionDirector
from Networking.send_message_to_client import send_message_to_client
from Networking import ports
import json
import time
#-----------------------------------------------------------
# todo: handle messages from Heimdall
#
def callback(data):
	json_data = json.loads(data)
	command = json_data["command"]

	print "\nreceived "+command +" message from Heimdall"
	print json_data

	

	# recieved 50 top waypoints
	# talk with mission director to send new waypoints
	# mission director needs to be able to verify points are inside the map

	if command == "send_image_path":
		time.sleep(10)
		send_message_to_client(json.dumps(json_data),ports.outport_PlaneOBC)
		print "forwarded message from MissionDirector to PlaneOBC"


