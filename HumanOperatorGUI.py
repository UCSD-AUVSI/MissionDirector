"""
Please! See http://www.tutorialspoint.com/python/tk_button.htm for some guidance on managing this GUI

TODO: check that there's any input in the entry field before pressing the button
TODO: make a help window - panel, tab...something
TODO: color status?
TODO: Flight time?
TODO: Graphic image of the gimbal angle
TODO: Status labels that change properly

"""
#using Tkinter so anyone with Python installed can run it immediately
from Tkinter import * 
import tkMessageBox


# import MissionDirector networking stuff
from Networking.send_message_to_client import send_message_to_client
from Networking import ports
import json
import threading, time
from Networking import server_multiport
ListenerToMissionDirectorServer = server_multiport.server()
TryingToStartMissionDirectorServer = False

def CallbackFromMissionDirector(data, FromIPaddr):
	# this needs to be a common interface between all UCSD AUVSI software parts: MissionDirector, Heimdall, NewOnboardSuite, etc.
	json_data = json.loads(data)
	cmd = json_data["cmd"]
	args = json_data["args"]
	if cmd == "status":
		print("Status from "+args["from"]+": "+args["message"])

def ThreadedListenToMissionDirectorMainServer(ipaddr):
	global ListenerToMissionDirectorServer
	global TryingToStartMissionDirectorServer
	ports_and_callbacks = [(ports.outport_HumanOperator, CallbackFromMissionDirector, server_multiport.SSLSecurityDetails(False))]
	ListenerToMissionDirectorServer.stop()
	ListenerToMissionDirectorServer.start(ports_and_callbacks, ipaddr, False, False) # Start server in the background
	time.sleep(1)
	if ListenerToMissionDirectorServer.CheckAllSocketsBound() == False:
		TryingToStartMissionDirectorServer = False

def StartListenerToMissionDirectorMainServer(ipaddr):
	global TryingToStartMissionDirectorServer
	if TryingToStartMissionDirectorServer == False:
		TryingToStartMissionDirectorServer = True
		thread = threading.Thread(target=ThreadedListenToMissionDirectorMainServer, args=(ipaddr,))
		thread.daemon = True
		thread.start()

#To initialize Tkinter, need to create a Tk root widget, 
#which is a window with a title bar and other decoration provided by window manager
#root widget has to be created before any other widgets and can only be one root widget
root = Tk()

def TryConvertStringToJSON(givenstring):
	try:
		return json.loads(givenstring)
	except ValueError:
		return givenstring

def StartMyListenerToMissionControl():
	myIPaddr = humanOpMyIPVar.get()
	if len(myIPaddr) != 0:
		print("starting listener to MissionControl")
		StartListenerToMissionDirectorMainServer(myIPaddr)
	else:
		print("please enter this machine\'s static IP address")

def missionDirectorIPConnect():
	MDipaddr = mDIPAVar.get()
	if len(MDipaddr) != 0:
		hellomsg = {}
		hellomsg["cmd"] = "status"
		hellomsg["args"] = {"hello":"ask"}
		send_message_to_client(json.dumps(hellomsg), ports.listenport_HumanOperator, MDipaddr)

def missionDirectorSend():
	cmd = missionDirectorVarCMD.get()
	args = TryConvertStringToJSON(missionDirectorVarARG.get())
	if len(cmd) == 0:
		print"Please enter command / args"
	else:
		mdmsg = {}
		mdmsg["cmd"] = cmd
		mdmsg["args"] = args
		send_message_to_client(json.dumps(mdmsg), ports.listenport_HumanOperator, mDIPAVar.get())

def planeOBCIPConnect():
	#todo: update gui when a reply is received?
	remotemsg = {}
	remotemsg["cmd"] = "status"
	remotemsg["args"] = {"hello":"ask"}
	fwdmsg = {}
	fwdmsg["cmd"] = "planeobc:"
	fwdmsg["args"] = {"message":json.dumps(remotemsg),"ip":planeOBCIPVar.get()}
	send_message_to_client(json.dumps(fwdmsg), ports.listenport_HumanOperator, mDIPAVar.get())

def planeOBCSend():
	cmd = planeOBCVarCMD.get()
	args = TryConvertStringToJSON(planeOBCVarARG.get())
	if len(cmd) == 0:
		print"Please enter command / args"
	else:
		remotemsg = {}
		remotemsg["cmd"] = cmd
		remotemsg["args"] = args
		fwdmsg = {}
		fwdmsg["cmd"] = "planeobc:"
		fwdmsg["args"] = {"message":json.dumps(remotemsg),"ip":planeOBCIPVar.get()}
		send_message_to_client(json.dumps(fwdmsg), ports.listenport_HumanOperator, mDIPAVar.get())

def arduinoQueryButtonAction():
	remotemsg = {}
	remotemsg["cmd"] = "status"
	remotemsg["args"] = {"arduino":"arduino"}
	fwdmsg = {}
	fwdmsg["cmd"] = "planeobc:"
	fwdmsg["args"] = {"message":json.dumps(remotemsg),"ip":planeOBCIPVar.get()}
	send_message_to_client(json.dumps(fwdmsg), ports.listenport_HumanOperator, mDIPAVar.get())

def heimdallIPConnect():
	#todo: update gui when a reply is received?
	remotemsg = {}
	remotemsg["cmd"] = "status"
	remotemsg["args"] = {"hello":"ask"}
	fwdmsg = {}
	fwdmsg["cmd"] = "heimdall:"
	fwdmsg["args"] = {"message":json.dumps(remotemsg),"ip":heimdallIPVar.get()}
	send_message_to_client(json.dumps(fwdmsg), ports.listenport_HumanOperator, mDIPAVar.get()) #forward message to Heimdall through the MissionDirector

def heimdallSend():
	cmd = heimdallVarCMD.get()
	args = TryConvertStringToJSON(heimdallVarARG.get())
	if len(cmd) == 0:
		print"Please enter command / args"
	else:
		remotemsg = {}
		remotemsg["cmd"] = cmd
		remotemsg["args"] = args
		fwdmsg = {}
		fwdmsg["cmd"] = "heimdall:"
		fwdmsg["args"] = {"message":json.dumps(remotemsg),"ip":heimdallIPVar.get()}
		send_message_to_client(json.dumps(fwdmsg), ports.listenport_HumanOperator, mDIPAVar.get())

def mavProxyIPConnect():
	someVar = mavProxyIPVar.get()
	if(someVar == ""):
		print"Please enter something"
	else:
		#Put method call here
		print "Currenlty connected to: ", someVar
def mavProxySend():
	cmd = mavProxyVarCMD.get()
	args = mavProxyVarARG.get()
	if len(cmd) == 0:
		print"Please enter command / args"
	else:
		#Put method call here
		print "Message to Mav Proxy:", someVar

def interoperabilityIPConnect():
	someVar = interoperabilityIPVar.get()
	if(someVar == ""):
		print"Please enter something"
	else:
		#Put method call here
		print "Currenlty connected to: ", someVar
def interoperabilitySend():
	cmd = interoperabilityVarCMD.get()
	args = interoperabilityVarARG.get()
	if len(cmd) == 0:
		print"Please enter command / args"
	else:
		#Put method call here
		print "Message to Mav Proxy:", someVar

def currentGimbalAngleSet():
	someVar = gimbalAngleVar.get()
	if(someVar == ""):
		print"Please enter something"
	else:
		#Put method call here
		print "Gimbal angle set to:", someVar

#Confirmation windows
def confirmBeginMission():
	result = tkMessageBox.askquestion("Begin Mission?", "Please confirm that you wish to begin flight")
	if result == 'yes':
		print "Beginning mission"
		#put method calls here	
	else:
		print "Did not begin mission"

def confirmEndMission():
	result = tkMessageBox.askquestion("End Mission?", "Please confirm mission termination")
	if result == 'yes':
		print "Ending mission. Landing plane"
		#put method calls here
	else:
		print "Did not end mission"

def confirmBeginImaging():
	result = tkMessageBox.askquestion("Begin Imaging?", "Please confirm that you with to begin imaging")
	if result == 'yes':
		print "Beginning imaging..."
		#put method calls here
		remotemsg = {}
		remotemsg["cmd"] = "imaging"
		remotemsg["args"] = {"start":" "}
		fwdmsg = {}
		fwdmsg["cmd"] = "planeobc:"
		fwdmsg["args"] = {"message":json.dumps(remotemsg),"ip":planeOBCIPVar.get()}
		send_message_to_client(json.dumps(fwdmsg), ports.listenport_HumanOperator, mDIPAVar.get())
	else:
		print "Did not start imaging"
			
def confirmStopImaging():
	result = tkMessageBox.askquestion("Stop Imaging?", "Please confirm that you with to end imaging")
	if result == 'yes':
		print "Stopping imaging"
		#put method calls here
		remotemsg = {}
		remotemsg["cmd"] = "imaging"
		remotemsg["args"] = {"stop":" "}
		fwdmsg = {}
		fwdmsg["cmd"] = "planeobc:"
		fwdmsg["args"] = {"message":json.dumps(remotemsg),"ip":planeOBCIPVar.get()}
		send_message_to_client(json.dumps(fwdmsg), ports.listenport_HumanOperator, mDIPAVar.get())
	else:
		print "Did not stop imaging"

def confirmSendImagesToJudges():
	result = tkMessageBox.askquestion("Send images to judges?", "Please confirm that you wish to send captured images for judging")
	if result == 'yes':
		print "Sending Images"
		#put method calls here
	else:
		print "Did not send images to judges"

def confirmGetReimagingWayPoints():
	result = tkMessageBox.askquestion("Get reimaging waypoints?", "Please confirm that you with to get reimaging waypoints")
	if result == 'yes':
		print "Reimaging waypoints"
		#put method calls here
	else:
		print "Did not reimage waypoints"

def handler():
    #result = tkMessageBox.askquestion("Quit?", "Are you sure you want to quit? This will end the mission.")
    if True: # result == 'yes':
	global ListenerToMissionDirectorServer
	ListenerToMissionDirectorServer.stop()
        root.quit()
    else:
    	print "Did not end mission"

humanOpMyIPVar = StringVar()
mDIPAVar = StringVar()
missionDirectorVarCMD = StringVar()
missionDirectorVarARG = StringVar()
planeOBCIPVar = StringVar()
planeOBCVarCMD = StringVar()
planeOBCVarARG = StringVar()
heimdallIPVar = StringVar()
heimdallVarCMD = StringVar()
heimdallVarARG = StringVar()
mavProxyIPVar = StringVar()
mavProxyVarCMD = StringVar()
mavProxyVarARG = StringVar()
interoperabilityIPVar = StringVar()
interoperabilityVarCMD = StringVar()
interoperabilityVarARG = StringVar()
gimbalAngleVar = StringVar()

#Name of panel
root.title("UCSD AUVSI Mission Control Operator GUI")	
root.protocol("WM_DELETE_WINDOW", handler)

CommandEntryCOLUMN = 1
ArgEntryCOLUMN = 2
BUTTONSCOLUMN = 3
StatusCOLUMN = 4

##Headers
systemTitle = Label(root, text = "System", font = "bold").grid(row = 0, column = 0)

systemTitle = Label(root, text = "cmd", font = "bold").grid(row = 0, column = 1)
systemTitle = Label(root, text = "arg(s)", font = "bold").grid(row = 0, column = 2)

#systemStatus = Label(root, text = "Status", width = 15, font = "bold").grid(row = 0, column = StatusCOLUMN)
#System Names
rowiter = 1
humanOpMyIP = Label(root, relief = RIDGE, text = "My HumanOperator IP", width = 18).grid(row= rowiter, column = 0)
rowiter += 1
mDIPA = Label(root, relief = RIDGE, text = "MissionControl IP", width = 18).grid(row= rowiter, column = 0)
rowiter += 1
missionDirector = Label(root, relief = RIDGE, text = "MissionControl", width = 18).grid(row=rowiter, column = 0)
rowiter += 1
planeOBCIP = Label(root, relief = RIDGE, text = "PlaneOBC IP", width = 18).grid(row=rowiter, column = 0)
rowiter += 1
planeOBC = Label(root, relief = RIDGE, text = "PlaneOBC", width = 18).grid(row=rowiter, column = 0)
rowiter += 1
heimdallIP = Label(root, relief = RIDGE, text = "Heimdall IP", width = 18).grid(row=rowiter, column = 0)
rowiter += 1
heimdall = Label(root, relief = RIDGE, text = "Heimdall", width = 18).grid(row=rowiter, column = 0)
rowiter += 1
mavProxyIP = Label(root, relief = RIDGE, text = "MissonPlanner IP", width = 18).grid(row = rowiter, column = 0)
rowiter += 1
mavProxy = Label(root, relief = RIDGE, text = "MissionPlanner", width = 18).grid(row = rowiter, column = 0)
rowiter += 1
interoperabilityIP = Label(root, relief = RIDGE, text = "Interoperability URL", width = 18).grid(row = rowiter, column = 0)
rowiter += 1
interoperability = Label(root, relief = RIDGE, text = "Interoperability", width = 18).grid(row = rowiter, column = 0)

#gimbalAngle = Label(root, relief = RIDGE, text = "Current Gimbal Angle", width = 18).grid(row = 10, column = 0)

"""
#Status Labels
mDIPAStatus = Label(root, text = "Not connected", width = 30).grid(row=1, column = StatusCOLUMN)
missionDirectorStatus = Label(root, text = "Default Status").grid(row=2, column = StatusCOLUMN)
planeOBCIPStatus = Label(root, text = "Not connected").grid(row=3, column = StatusCOLUMN)
planeOBCStatus = Label(root, text = "Default Status", width = 30).grid(row=4, column = StatusCOLUMN)
heimdallIPStatus = Label(root, text = "Not connected").grid(row=5, column = StatusCOLUMN)
heimdallStatus = Label(root, text = "Default Status").grid(row=6, column = StatusCOLUMN)
mavProxyIPStatus = Label(root, text = "Not connected").grid(row=7, column = StatusCOLUMN)
mavProxyStatus  = Label(root, text = "Default Status").grid(row=8, column = StatusCOLUMN)
gimbalStatus = Label(root, text = "Default Status").grid(row = 9, column = StatusCOLUMN)
flightStatus = Label(root, text = "Default Status").grid(row = 10, column = StatusCOLUMN)
imagingStatus = Label(root, text = "Default Status").grid(row = 11, column = StatusCOLUMN)
communicationStatus = Label(root, text = "Default Status").grid(row = 12, column = StatusCOLUMN)
"""

#####Entry fields
rowiter = 1
humanOpMyIPEntry = Entry(root, width = 30, textvariable = humanOpMyIPVar).grid(row = rowiter, column = ArgEntryCOLUMN)
rowiter += 1
mDIPAEntry = Entry(root, width = 30, textvariable = mDIPAVar).grid(row = rowiter, column = ArgEntryCOLUMN)
rowiter += 1
missionDirectorEntryCMD = Entry(root, width = 30, textvariable = missionDirectorVarCMD).grid(row = rowiter, column = CommandEntryCOLUMN)
missionDirectorEntryARG = Entry(root, width = 30, textvariable = missionDirectorVarARG).grid(row = rowiter, column = ArgEntryCOLUMN)
rowiter += 1
planeOBCIPEntry = Entry(root, width = 30, textvariable = planeOBCIPVar).grid(row = rowiter, column = ArgEntryCOLUMN)
rowiter += 1
planeOBCEntryCMD = Entry(root, width = 30, textvariable = planeOBCVarCMD).grid(row = rowiter, column = CommandEntryCOLUMN)
planeOBCEntryARG = Entry(root, width = 30, textvariable = planeOBCVarARG).grid(row = rowiter, column = ArgEntryCOLUMN)
rowiter += 1
heimdallIPEntry = Entry(root, width = 30, textvariable = heimdallIPVar).grid(row = rowiter, column = ArgEntryCOLUMN)
rowiter += 1
heimdallEntryCMD = Entry(root, width = 30, textvariable = heimdallVarCMD).grid(row = rowiter, column = CommandEntryCOLUMN)
heimdallEntryARG = Entry(root, width = 30, textvariable = heimdallVarARG).grid(row = rowiter, column = ArgEntryCOLUMN)
rowiter += 1
mavProxyIPEntry = Entry(root, width = 30, textvariable = mavProxyIPVar).grid(row = rowiter, column = ArgEntryCOLUMN)
rowiter += 1
mavProxyEntryCMD = Entry(root, width = 30, textvariable = mavProxyVarCMD).grid(row = rowiter, column = CommandEntryCOLUMN)
mavProxyEntryARG = Entry(root, width = 30, textvariable = mavProxyVarARG).grid(row = rowiter, column = ArgEntryCOLUMN)
rowiter += 1
interoperabilityIPEntry = Entry(root, width = 30, textvariable = interoperabilityIPVar).grid(row = rowiter, column = ArgEntryCOLUMN)
rowiter += 1
interoperabilityEntryCMD = Entry(root, width = 30, textvariable = interoperabilityVarCMD).grid(row = rowiter, column = CommandEntryCOLUMN)
interoperabilityEntryARG = Entry(root, width = 30, textvariable = interoperabilityVarARG).grid(row = rowiter, column = ArgEntryCOLUMN)

#gimbalEntry = Entry(root, width = 30, text = gimbalAngleVar).grid(row = 9, column = CommandEntryCOLUMN)

#####Buttons
connect11Button = Button(root, text = "Start", width = 5, command = StartMyListenerToMissionControl).grid(row = 1, column = BUTTONSCOLUMN)
connect22Button = Button(root, text = "Connect", width = 5, command = missionDirectorIPConnect).grid(row = 2, column = BUTTONSCOLUMN)
send22Button = Button(root, text = "Send", width = 5, command = missionDirectorSend).grid(row = 3, column = BUTTONSCOLUMN)
connect33Button = Button(root, text = "Connect", width = 5, command = planeOBCIPConnect).grid(row = 4, column = BUTTONSCOLUMN)
send33Button = Button(root, text = "Send", width = 5, command = planeOBCSend).grid(row = 5, column = BUTTONSCOLUMN)
connect44Button = Button(root, text = "Connect", width = 5, command = heimdallIPConnect).grid(row = 6, column = BUTTONSCOLUMN)
send44Button = Button(root, text = "Send", width = 5, command = heimdallSend).grid(row = 7, column = BUTTONSCOLUMN)
connect55Button = Button(root, text = "Connect", width =5, command = mavProxyIPConnect).grid(row = 8, column = BUTTONSCOLUMN)
send55Button = Button(root, text = "Send", width= 5, command = mavProxySend).grid(row = 9, column = BUTTONSCOLUMN)
connect66Button = Button(root, text = "Connect", width =5, command = interoperabilityIPConnect).grid(row = 10, column = BUTTONSCOLUMN)
send66Button = Button(root, text = "Send", width= 5, command = interoperabilitySend).grid(row = 11, column = BUTTONSCOLUMN)

#send7Button = Button(root, text = "Set", width = 5, command = currentGimbalAngleSet).grid(row = 9, column = BUTTONSCOLUMN)

send7Buttonblanklabel = Label(root, text = " ", font = "bold").grid(row = 11, column = BUTTONSCOLUMN)

"""beginMissionButton = Button(root, text = "Begin Mission", width = 15, 
	command = confirmBeginMission).grid(row = 10, column = 0)
endMissionButton = Button(root, text = "End Mission", width = 15, 
	command = confirmEndMission).grid(row = 10, column = 1)
"""
startImagingButton = Button(root, text = "Start imaging", width = 15, 
	command = confirmBeginImaging).grid(row = 12, column = 0)
stopImagingButton = Button(root, text = "Stop imaging", width = 18, 
	command = confirmStopImaging).grid(row = 12, column = 1)
sendImagesButton = Button(root, text = "Save ADLC targets", width = 15, 
	command = confirmSendImagesToJudges).grid(row = 13, column = 0)
getReimageWaypointsButton = Button(root, text = "Get re-image waypoints", width = 18, 
	command = confirmGetReimagingWayPoints).grid(row = 13, column = 1)

arduinoQueryButton = Button(root, text = "Query OB Arduino Status", width = 20, 
	command = arduinoQueryButtonAction).grid(row = 12, column = 2)
arduinoQueryButton = Button(root, text = "Query OB Gimbal Status", width = 20, 
	command = arduinoQueryButtonAction).grid(row = 13, column = 2)

root.mainloop(), 










