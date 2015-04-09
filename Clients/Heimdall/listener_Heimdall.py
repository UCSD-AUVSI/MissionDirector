
import MissionDirector
import json

#-----------------------------------------------------------
# todo: handle messages from Heimdall
#
def callback(data):
	print "received message from Heimdall: \"" + str(data) + "\""
	print "todo: handle messages from Heimdall"

	# recieved 50 top waypoints
	# talk with mission director to send new waypoints
	# mission director needs to be able to verify points are inside the map

