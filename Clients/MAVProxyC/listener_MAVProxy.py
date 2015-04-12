
import MissionDirector
from Networking.send_message_to_client import send_message_to_client
from Networking import ports


#-----------------------------------------------------------
# Manage messages from MAVProxy's "mdlink" module
#
def callback(data):
	print "received message from MAVProxy: \"" + str(data) + "\""
	print "todo: Update MissionDirector values such as \"time_elapsed\" or \"gps_location\",\n\tand tell it about events such as \"WaypointReached\""
	
	if str(data) == "hello":
		print("Mission Director received \"hello\" message from MAVProxy; replying")
		
		#send the same message back to MAVProxy
		send_message_to_client(datastr, ports.outport_MAVProxy)


