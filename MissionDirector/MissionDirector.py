
class MissionDirector:
	
	def __init__(self):
		self.status = "Landed"
		self.waypoints = []
	
	def add_waypoint(self, waypoint):
		self.waypoints.append(waypoint)
	
	#--------------------------
	# todo:
	# 
	# keep track of mission state
	# make a checklist of things to do, in order
	#
	# for example: (there's more than this, such as off-axis target)
	#
	# (1) takeoff
	# (2) initial assigned waypoints
	# (3) search area waypoints
	# (4) SRIC station loiter and communication
	# (5) upload new search area waypoints to re-image certain objects
	# (6) land the plane

