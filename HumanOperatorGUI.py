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
ListenerToMissionDIrectorServerAlreadyStartedAndThisIsItsIP = ""

def CallbackFromMissionDirector(data, FromIPaddr):
	# this needs to be a common interface between all UCSD AUVSI software parts: MissionDirector, Heimdall, NewOnboardSuite, etc.
	json_data = json.loads(data)
	cmd = json_data["cmd"]
	args = json_data["args"]
	if cmd == "status":
		if "from" in args and args["from"] == "PlaneOBC":
			argsmessage = args["message"]
			argsmessagejson = json.loads(argsmessage)
			if "cpu" in argsmessagejson:
				cpuinfo = json.loads(argsmessagejson["cpu"])
				def CompactifyRedundantList(lst):
					retlst = []
					for lval in lst:
						if lval not in retlst:
							retlst.append(lval)
					return retlst
				freqslist0 = CompactifyRedundantList(cpuinfo[1][0])
				freqslist1 = CompactifyRedundantList(cpuinfo[1][1])
				governors = CompactifyRedundantList(cpuinfo[1][2])
				StatusClockUpdaterLock.acquire() #good multithreading practice
				lastreceivedCPUtemp.set(str(cpuinfo[0]))
				lastreceivedCPUtempTime.set("0")
				lastreceivedCPUfreq.set(str(freqslist0)+" "+str(freqslist1)+" "+str(governors))
				lastreceivedCPUfreqTime.set("0")
				StatusClockUpdaterLock.release()
			if "arduino" in argsmessagejson:
				StatusClockUpdaterLock.acquire() #good multithreading practice
				lastreceivedArduinoStatus.set(str(argsmessagejson["arduino"]))
				lastreceivedArduinoStatusTime.set("0")
				StatusClockUpdaterLock.release()
			print("Status from "+args["from"]+": "+argsmessage)
		else:
				print("Status from MissionDirector: "+str(args))

StatusClockUpdaterStarted = False
StatusClockUpdaterLock = threading.Lock()
StatusClockUpdaterTimeoutHideTime = 60
StatusClockUpdaterGrayoutTime = 30

def TryCastInt(ival):
	try:
		aaa = int(ival)
		return True
	except:
		return False

def UpdateAClockVar(var, var2data, varlabel, vartimelabel):
	if TryCastInt(var.get()):
		varint = int(var.get())
		if varint < StatusClockUpdaterGrayoutTime:
			var.set(str(varint+1))
		elif StatusClockUpdaterTimeoutHideTime:
			var.set(str(varint+1))
			varlabel.config(foreground='#808080')
			vartimelabel.config(foreground='#808080')
		else:
			var.set("")
			var2data.set("")

def ThreadLoopUpdateStatusClocks____():
	StatusClockUpdaterStarted = True
	print("StatusClockUpdater has been started!")
	while True:
		StatusClockUpdaterLock.acquire()
		UpdateAClockVar(lastreceivedCPUtempTime, lastreceivedCPUtemp, lastreceivedCPUtempLabel, lastreceivedCPUtempTimeLabel)
		UpdateAClockVar(lastreceivedCPUfreqTime, lastreceivedCPUfreq, lastreceivedCPUfreqLabel, lastreceivedCPUfreqTimeLabel)
		UpdateAClockVar(lastreceivedArduinoStatusTime, lastreceivedArduinoStatus, lastreceivedArduinoStatusLabel, lastreceivedArduinoStatusTimeLabel)
		StatusClockUpdaterLock.release()
		time.sleep(1)

def StartThreadedUpdateStatusClocks():
	if StatusClockUpdaterStarted == False:
		thread = threading.Thread(target=ThreadLoopUpdateStatusClocks____)
		thread.daemon = True
		thread.start()

def ThreadedListenToMissionDirectorMainServer(ipaddr):
	global ListenerToMissionDirectorServer
	global TryingToStartMissionDirectorServer
	global ListenerToMissionDIrectorServerAlreadyStartedAndThisIsItsIP
	print("starting listener to MissionControl")
	ports_and_callbacks = [(ports.outport_HumanOperator, CallbackFromMissionDirector, server_multiport.SSLSecurityDetails(False))]
	ListenerToMissionDirectorServer.stop()
	ListenerToMissionDirectorServer.start(ports_and_callbacks, ipaddr, False, False) # Start server in the background
	time.sleep(0.5)
	if ListenerToMissionDirectorServer.CheckAllSocketsBound() == False:
		TryingToStartMissionDirectorServer = False
	else:
		ListenerToMissionDIrectorServerAlreadyStartedAndThisIsItsIP = str(ipaddr)

def StartListenerToMissionDirectorMainServer(ipaddr):
	global TryingToStartMissionDirectorServer
	global ListenerToMissionDIrectorServerAlreadyStartedAndThisIsItsIP
	if len(ListenerToMissionDIrectorServerAlreadyStartedAndThisIsItsIP) > 0:
		print("listener already started on IP \'"+ListenerToMissionDIrectorServerAlreadyStartedAndThisIsItsIP+"\'")
		return
	if TryingToStartMissionDirectorServer == False:
		StartThreadedUpdateStatusClocks() #start this too
		TryingToStartMissionDirectorServer = True
		thread = threading.Thread(target=ThreadedListenToMissionDirectorMainServer, args=(ipaddr,))
		thread.daemon = True
		thread.start()

#To initialize Tkinter, need to create a Tk root widget, 
#which is a window with a title bar and other decoration provided by window manager
#root widget has to be created before any other widgets and can only be one root widget
root = Tk()
padamtX = 4
padamtY = 8
topframe = Frame(root, width=900, height=600)
topframe.grid(row=0, column=0, padx=padamtX, pady=padamtY)
middleFrame = Frame(root, width=900, height=600)
middleFrame.grid(row=1, column=0, padx=padamtX, pady=padamtY)
bottomframe = Frame(root, width=900, height=600)
bottomframe.grid(row=2, column=0, padx=padamtX, pady=padamtY)

def TryConvertStringToJSON(givenstring):
	try:
		return json.loads(givenstring)
	except ValueError:
		return givenstring

def StartMyListenerToMissionControl():
	myIPaddr = humanOpMyIPVar.get()
	if len(myIPaddr) != 0:
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
	remotemsg["args"] = {"arduino":"ask"}
	fwdmsg = {}
	fwdmsg["cmd"] = "planeobc:"
	fwdmsg["args"] = {"message":json.dumps(remotemsg),"ip":planeOBCIPVar.get()}
	send_message_to_client(json.dumps(fwdmsg), ports.listenport_HumanOperator, mDIPAVar.get())

def QueryCPUTempButtonAction():
	remotemsg = {}
	remotemsg["cmd"] = "status"
	remotemsg["args"] = {"cpu":"ask"}
	fwdmsg = {}
	fwdmsg["cmd"] = "planeobc:"
	fwdmsg["args"] = {"message":json.dumps(remotemsg),"ip":planeOBCIPVar.get()}
	send_message_to_client(json.dumps(fwdmsg), ports.listenport_HumanOperator, mDIPAVar.get())

def QueryCPUFreqButtonAction():
	QueryCPUTempButtonAction() #both pieces of info are packed into the same message

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

lastreceivedCPUfreq = StringVar()
lastreceivedCPUtemp = StringVar()
lastreceivedArduinoStatus = StringVar()
lastreceivedCPUfreqTime = StringVar()
lastreceivedCPUtempTime = StringVar()
lastreceivedArduinoStatusTime = StringVar()

#Name of panel
root.title("UCSD AUVSI Mission Control Operator GUI")	
root.protocol("WM_DELETE_WINDOW", handler)

CommandEntryCOLUMN = 1
ArgEntryCOLUMN = 2
BUTTONSCOLUMN = 3
StatusCOLUMN = 4

##Headers
Label(topframe, text = "System", font = "bold").grid(row = 0, column = 0)
Label(topframe, text = "cmd", font = "bold").grid(row = 0, column = 1)
Label(topframe, text = "arg(s)", font = "bold").grid(row = 0, column = 2)

#systemStatus = Label(topframe, text = "Status", width = 15, font = "bold").grid(row = 0, column = StatusCOLUMN)
#System Names
rowiter = 1
Label(topframe, relief = RIDGE, text = "My HumanOperator IP", width = 18).grid(row= rowiter, column = 0)
rowiter += 1
Label(topframe, relief = RIDGE, text = "MissionControl IP", width = 18).grid(row= rowiter, column = 0)
rowiter += 1
Label(topframe, relief = RIDGE, text = "MissionControl", width = 18).grid(row=rowiter, column = 0)
rowiter += 1
Label(topframe, relief = RIDGE, text = "PlaneOBC IP", width = 18).grid(row=rowiter, column = 0)
rowiter += 1
Label(topframe, relief = RIDGE, text = "PlaneOBC", width = 18).grid(row=rowiter, column = 0)
rowiter += 1
Label(topframe, relief = RIDGE, text = "Heimdall IP", width = 18).grid(row=rowiter, column = 0)
rowiter += 1
Label(topframe, relief = RIDGE, text = "Heimdall", width = 18).grid(row=rowiter, column = 0)
rowiter += 1
Label(topframe, relief = RIDGE, text = "MissonPlanner IP", width = 18).grid(row = rowiter, column = 0)
rowiter += 1
Label(topframe, relief = RIDGE, text = "MissionPlanner", width = 18).grid(row = rowiter, column = 0)
rowiter += 1
Label(topframe, relief = RIDGE, text = "Interoperability URL", width = 18).grid(row = rowiter, column = 0)
rowiter += 1
Label(topframe, relief = RIDGE, text = "Interoperability", width = 18).grid(row = rowiter, column = 0)

#gimbalAngle = Label(topframe, relief = RIDGE, text = "Current Gimbal Angle", width = 18).grid(row = 10, column = 0)

"""
#Status Labels
mDIPAStatus = Label(topframe, text = "Not connected", width = 30).grid(row=1, column = StatusCOLUMN)
missionDirectorStatus = Label(topframe, text = "Default Status").grid(row=2, column = StatusCOLUMN)
planeOBCIPStatus = Label(topframe, text = "Not connected").grid(row=3, column = StatusCOLUMN)
planeOBCStatus = Label(topframe, text = "Default Status", width = 30).grid(row=4, column = StatusCOLUMN)
heimdallIPStatus = Label(topframe, text = "Not connected").grid(row=5, column = StatusCOLUMN)
heimdallStatus = Label(topframe, text = "Default Status").grid(row=6, column = StatusCOLUMN)
mavProxyIPStatus = Label(topframe, text = "Not connected").grid(row=7, column = StatusCOLUMN)
mavProxyStatus  = Label(topframe, text = "Default Status").grid(row=8, column = StatusCOLUMN)
gimbalStatus = Label(topframe, text = "Default Status").grid(row = 9, column = StatusCOLUMN)
flightStatus = Label(topframe, text = "Default Status").grid(row = 10, column = StatusCOLUMN)
imagingStatus = Label(topframe, text = "Default Status").grid(row = 11, column = StatusCOLUMN)
communicationStatus = Label(topframe, text = "Default Status").grid(row = 12, column = StatusCOLUMN)
"""

#####Entry fields
rowiter = 1
Entry(topframe, width = 30, textvariable = humanOpMyIPVar).grid(row = rowiter, column = ArgEntryCOLUMN)
rowiter += 1
Entry(topframe, width = 30, textvariable = mDIPAVar).grid(row = rowiter, column = ArgEntryCOLUMN)
rowiter += 1
Entry(topframe, width = 30, textvariable = missionDirectorVarCMD).grid(row = rowiter, column = CommandEntryCOLUMN)
Entry(topframe, width = 30, textvariable = missionDirectorVarARG).grid(row = rowiter, column = ArgEntryCOLUMN)
rowiter += 1
Entry(topframe, width = 30, textvariable = planeOBCIPVar).grid(row = rowiter, column = ArgEntryCOLUMN)
rowiter += 1
Entry(topframe, width = 30, textvariable = planeOBCVarCMD).grid(row = rowiter, column = CommandEntryCOLUMN)
Entry(topframe, width = 30, textvariable = planeOBCVarARG).grid(row = rowiter, column = ArgEntryCOLUMN)
rowiter += 1
Entry(topframe, width = 30, textvariable = heimdallIPVar).grid(row = rowiter, column = ArgEntryCOLUMN)
rowiter += 1
Entry(topframe, width = 30, textvariable = heimdallVarCMD).grid(row = rowiter, column = CommandEntryCOLUMN)
Entry(topframe, width = 30, textvariable = heimdallVarARG).grid(row = rowiter, column = ArgEntryCOLUMN)
rowiter += 1
Entry(topframe, width = 30, textvariable = mavProxyIPVar).grid(row = rowiter, column = ArgEntryCOLUMN)
rowiter += 1
Entry(topframe, width = 30, textvariable = mavProxyVarCMD).grid(row = rowiter, column = CommandEntryCOLUMN)
Entry(topframe, width = 30, textvariable = mavProxyVarARG).grid(row = rowiter, column = ArgEntryCOLUMN)
rowiter += 1
Entry(topframe, width = 30, textvariable = interoperabilityIPVar).grid(row = rowiter, column = ArgEntryCOLUMN)
rowiter += 1
Entry(topframe, width = 30, textvariable = interoperabilityVarCMD).grid(row = rowiter, column = CommandEntryCOLUMN)
Entry(topframe, width = 30, textvariable = interoperabilityVarARG).grid(row = rowiter, column = ArgEntryCOLUMN)

#Entry(topframe, width = 30, text = gimbalAngleVar).grid(row = 9, column = CommandEntryCOLUMN)

#####Buttons
Button(topframe, text = "Start", width = 5, command = StartMyListenerToMissionControl).grid(row = 1, column = BUTTONSCOLUMN)
Button(topframe, text = "Connect", width = 5, command = missionDirectorIPConnect).grid(row = 2, column = BUTTONSCOLUMN)
Button(topframe, text = "Send", width = 5, command = missionDirectorSend).grid(row = 3, column = BUTTONSCOLUMN)
Button(topframe, text = "Connect", width = 5, command = planeOBCIPConnect).grid(row = 4, column = BUTTONSCOLUMN)
Button(topframe, text = "Send", width = 5, command = planeOBCSend).grid(row = 5, column = BUTTONSCOLUMN)
Button(topframe, text = "Connect", width = 5, command = heimdallIPConnect).grid(row = 6, column = BUTTONSCOLUMN)
Button(topframe, text = "Send", width = 5, command = heimdallSend).grid(row = 7, column = BUTTONSCOLUMN)
Button(topframe, text = "Connect", width =5, command = mavProxyIPConnect).grid(row = 8, column = BUTTONSCOLUMN)
Button(topframe, text = "Send", width= 5, command = mavProxySend).grid(row = 9, column = BUTTONSCOLUMN)
Button(topframe, text = "Connect", width =5, command = interoperabilityIPConnect).grid(row = 10, column = BUTTONSCOLUMN)
Button(topframe, text = "Send", width= 5, command = interoperabilitySend).grid(row = 11, column = BUTTONSCOLUMN)

#Button(topframe, text = "Set", width = 5, command = currentGimbalAngleSet).grid(row = 9, column = BUTTONSCOLUMN)

Label(topframe, text = " ", font = "bold").grid(row = 11, column = BUTTONSCOLUMN)

"""beginMissionButton = Button(topframe, text = "Begin Mission", width = 15, 
	command = confirmBeginMission).grid(row = 10, column = 0)
endMissionButton = Button(topframe, text = "End Mission", width = 15, 
	command = confirmEndMission).grid(row = 10, column = 1)
"""
Button(middleFrame, text = "Start imaging", width = 15, command = confirmBeginImaging).grid(row = 12, column = 0)
Button(middleFrame, text = "Stop imaging", width = 18, command = confirmStopImaging).grid(row = 12, column = 1)
Button(middleFrame, text = "Save ADLC targets", width = 15, command = confirmSendImagesToJudges).grid(row = 13, column = 0)
Button(middleFrame, text = "Get re-image waypoints", width = 18, command = confirmGetReimagingWayPoints).grid(row = 13, column = 1)
Button(middleFrame, text = "Query OB Arduino Status", width = 20, command = arduinoQueryButtonAction).grid(row = 12, column = 2)
Button(middleFrame, text = "Query OB Gimbal Status", width = 20, command = arduinoQueryButtonAction).grid(row = 13, column = 2)
Button(middleFrame, text = "Query OB CPU Temperature", width = 20, command = QueryCPUTempButtonAction).grid(row = 12, column = 3)
Button(middleFrame, text = "Query OB CPU Frequency", width = 20, command = QueryCPUFreqButtonAction).grid(row = 13, column = 3)

#==========================================================================================================

Label(bottomframe, relief = RIDGE, text = "CPU TEMP", width = 10).grid(row=0, column=0)
lastreceivedCPUtempTimeLabel = Label(bottomframe, relief = RIDGE, textvariable = lastreceivedCPUtempTime, width = 10)
lastreceivedCPUtempTimeLabel.grid(row=0, column=1)
lastreceivedCPUtempLabel = Label(bottomframe, relief = RIDGE, textvariable = lastreceivedCPUtemp, width = 60)
lastreceivedCPUtempLabel.grid(row=0, column=2)

Label(bottomframe, relief = RIDGE, text = "CPU FREQ", width = 10).grid(row=1, column=0)
lastreceivedCPUfreqTimeLabel = Label(bottomframe, relief = RIDGE, textvariable = lastreceivedCPUfreqTime, width = 10)
lastreceivedCPUfreqTimeLabel.grid(row=1, column=1)
lastreceivedCPUfreqLabel = Label(bottomframe, relief = RIDGE, textvariable = lastreceivedCPUfreq, width = 60)
lastreceivedCPUfreqLabel.grid(row=1, column=2)

Label(bottomframe, relief = RIDGE, text = "ARDUINO", width = 10).grid(row=2, column=0)
lastreceivedArduinoStatusTimeLabel = Label(bottomframe, relief = RIDGE, textvariable = lastreceivedArduinoStatusTime, width = 10)
lastreceivedArduinoStatusTimeLabel.grid(row=2, column=1)
lastreceivedArduinoStatusLabel = Label(bottomframe, relief = RIDGE, textvariable = lastreceivedArduinoStatus, width = 60)
lastreceivedArduinoStatusLabel.grid(row=2, column=2)

root.mainloop(), 










