#
# These numbers were picked for no particular reason
#

listenport_HumanOperator  = 9980
outport_HumanOperator = 9979

listenport_Heimdall = 9981  #messages received FROM Heimdall TO MissionDirector
outport_Heimdall = 9986     #for messages sent FROM MissionDirector TO Heimdall

listenport_MAVProxy = 9982  #messages received FROM MAVProxy TO MissionDirector
outport_MAVProxy = 9983     #for messages sent FROM MissionDirector TO MAVProxy

listenport_PlaneOBC = 9984  #messages received FROM PlaneOBC TO MissionDirector
outport_PlaneOBC = 9985     #for messages sent FROM MissionDirector TO PlaneOBC
		#note: outport_PlaneOBC is a secure socket channel (i.e. SSL/TLS)

