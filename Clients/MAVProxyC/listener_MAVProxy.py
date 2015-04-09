
import MissionDirector
import json

#-----------------------------------------------------------
# Variables used by MAVProxy listener
#


#-----------------------------------------------------------
# Manage messages from MAVProxy's "mdlink" module
#
def callback(data):
	print "received message from MAVProxy: \"" + str(data) + "\""
	print "todo: Update MissionDirector values such as \"time_elapsed\" or \"gps_location\",\n\tand tell it about events such as \"WaypointReached\""
	json_data = json.loads(data)

