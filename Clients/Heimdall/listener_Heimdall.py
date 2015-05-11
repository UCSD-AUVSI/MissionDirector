
import MissionDirector
from Networking.send_message_to_client import send_message_to_client
from Networking import ports
import json
import time
#-----------------------------------------------------------
# todo: handle messages from Heimdall
#
def callback(data, FromIPaddr):
	json_data = json.loads(data)
	cmd = json_data["cmd"]

	print "\nreceived "+cmd+" message from Heimdall"
	print json_data

	

	# recieved 50 top waypoints
	# talk with mission director to send new waypoints
	# mission director needs to be able to verify points are inside the map

	if cmd == "send_image_path":
		time.sleep(10)
		send_message_to_client(json.dumps(json_data), ports.outport_PlaneOBC, ports.IPaddr_PlaneOBC)
		print "forwarded message from MissionDirector to PlaneOBC"


