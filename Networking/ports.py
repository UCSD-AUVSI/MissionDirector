#
# These numbers were picked for no particular reason
#

listenport_HumanOperator  = 9980  #messages received FROM HumanOperatorGUI TO MissionDirector
outport_HumanOperator = 9979      #for messages sent FROM MissionDirector TO HumanOperatorGUI
IPaddr_HumanOperator = "unknown"  #found at runtime

listenport_Heimdall = 9981  #messages received FROM Heimdall TO MissionDirector
outport_Heimdall = 9986     #for messages sent FROM MissionDirector TO Heimdall
IPaddr_Heimdall = "unknown"  #given at runtime by HumanOperatorGUI

listenport_MAVProxy = 9982  #messages received FROM MAVProxy TO MissionDirector
outport_MAVProxy = 9983     #for messages sent FROM MissionDirector TO MAVProxy
IPaddr_MAVProxy = "unknown"  #given at runtime by HumanOperatorGUI

PlaneOBC_use_secure_comms_boolean = True
PlaneOBC_secure_socket_is_connected = False
PlaneOBC_secure_socket = ""
PlaneOBC_listeningssldetails = ""
outport_PlaneOBC = 9985  #messages TO PlaneOBC FROM MissionDirector
listenport_PlaneOBC = 9984  #messages FROM PlaneOBC TO MissionDirector
IPaddr_PlaneOBC = "unknown"  #given at runtime by HumanOperatorGUI
		#note: PlaneOBC is a secure socket channel (i.e. SSL/TLS)
