
import MissionDirector
from Networking.send_message_to_client import send_message_to_client
from Networking import ports

from interoperability import globalvar_connection_interop as InterOP

#-----------------------------------------------------------
# Manage messages from MAVProxy's "mdlink" module, which currently does not use JSON
#
def callback(data, FromIPaddr):
	print "received message from MAVProxy: \"" + str(data) + "\""
	print "todo: Update MissionDirector values such as \"time_elapsed\" or \"gps_location\",\n\tand tell it about events such as \"WaypointReached\""
	
	json_data = json.loads(data)
	cmd = json_data["cmd"]	
	args = json_data["args"]

	if cmd == "telemdata":
		gps_data = args
		
		# update interop gps Data
		InterOP.connection.update_gps(gps_data)			
		# send the same message to Heimdall
		send_message_to_client(datastr, ports.outport_Heimdall, ports.IPaddr_Heimdall)


