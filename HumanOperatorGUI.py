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


# import MissionDirector networking stuff
from Networking.send_message_to_client import send_message_to_client
from Networking import ports
import json
import threading, time
from Networking import server_multiport
ListenerToMissionDirectorServer = server_multiport.server()
TryingToStartMissionDirectorServer = False
ListenerToMissionDIrectorServerAlreadyStartedAndThisIsItsIP = ""

def TryCastInt(ival):
	try:
		aaa = int(ival)
		return True
	except:
		return False

class ConnectionStatusLabel(object):
	def __init__(self, initialstr, row):
		self.strVar = StringVar()
		self.strVar.set(initialstr)
		self.MyLabel = Label(topframe, width = 30, relief = FLAT, textvariable = self.strVar)
		self.MyLabel.grid(row = row, column = CommandEntryCOLUMN)
		self.MyLabel.config(foreground='#505050')

class InfoStatusLabel(object):
	def __init__(self, name, row):
		self.lastTime = StringVar()
		self.lastStatus = StringVar()
		Label(bottomframe, relief = RIDGE, text = name, width = 10).grid(row=row, column=0)
		self.timeL = Label(bottomframe, relief = RIDGE, textvariable = self.lastTime, width = 10)
		self.timeL.grid(row=row, column=1)
		self.infoL = Label(bottomframe, relief = RIDGE, textvariable = self.lastStatus, width = 60)
		self.infoL.grid(row=row, column=2)

def UpdateAClockVar(labell):
	if TryCastInt(labell.lastTime.get()):
		varint = int(labell.lastTime.get())
		if varint < StatusClockUpdaterGrayoutTime:
			labell.lastTime.set(str(varint+1))
			labell.infoL.config(foreground='#000000')
			labell.timeL.config(foreground='#000000')
		elif varint < StatusClockUpdaterGrayoutTime22:
			labell.lastTime.set(str(varint+1))
			labell.infoL.config(foreground='#424242')
			labell.timeL.config(foreground='#424242')
		elif varint < StatusClockUpdaterTimeoutHideTime:
			labell.lastTime.set(str(varint+1))
			labell.infoL.config(foreground='#898989')
			labell.timeL.config(foreground='#898989')
		else:
			labell.lastTime.set("")
			labell.lastStatus.set("")

AllLabelsDict = {}
AllLabelsDict["CPUtemp"] = InfoStatusLabel("CPU TEMP",0)
AllLabelsDict["CPUfreq"] = InfoStatusLabel("CPU FREQ",1)
AllLabelsDict["Arduino"] = InfoStatusLabel("Arduino",2)
AllLabelsDict["DSLR"] = InfoStatusLabel("DSLR",3)
AllLabelsDict["telem"] = InfoStatusLabel("telem",4)

def CallbackFromMissionDirector(data, FromIPaddr):
	# this needs to be a common interface between all UCSD AUVSI software parts: MissionDirector, Heimdall, NewOnboardSuite, etc.
	json_data = json.loads(data)
	cmd = json_data["cmd"]
	args = json_data["args"]
	if cmd == "status":
		if "from" in args and args["from"] == "PlaneOBC":
			argsmessage = args["message"]
			argsmessagejson = json.loads(argsmessage)
			if "cpu-freq" in argsmessagejson:
				cpuinfo = json.loads(argsmessagejson["cpu-freq"])
				def CompactifyRedundantList(lst):
					retlst = []
					for lval in lst:
						if lval not in retlst:
							retlst.append(lval)
					return retlst
				freqslist0 = CompactifyRedundantList(cpuinfo[0])
				freqslist1 = CompactifyRedundantList(cpuinfo[1])
				governors = CompactifyRedundantList(cpuinfo[2])
				StatusClockUpdaterLock.acquire() #good multithreading practice
				AllLabelsDict["CPUfreq"].lastStatus.set(str(freqslist0)+" "+str(freqslist1)+" "+str(governors))
				AllLabelsDict["CPUfreq"].lastTime.set("0")
				StatusClockUpdaterLock.release()
			if "cpu-temp" in argsmessagejson:
				StatusClockUpdaterLock.acquire() #good multithreading practice
				AllLabelsDict["CPUtemp"].lastStatus.set(str(json.loads(argsmessagejson["cpu-temp"])))
				AllLabelsDict["CPUtemp"].lastTime.set("0")
				StatusClockUpdaterLock.release()
			if "arduino" in argsmessagejson:
				StatusClockUpdaterLock.acquire() #good multithreading practice
				AllLabelsDict["Arduino"].lastStatus.set(str(argsmessagejson["arduino"]))
				AllLabelsDict["Arduino"].lastTime.set("0")
				StatusClockUpdaterLock.release()
			if "DSLR" in argsmessagejson:
				StatusClockUpdaterLock.acquire() #good multithreading practice
				AllLabelsDict["DSLR"].lastStatus.set(str(argsmessagejson["DSLR"]))
				AllLabelsDict["DSLR"].lastTime.set("0")
				StatusClockUpdaterLock.release()
			if "telem" in argsmessagejson:
				StatusClockUpdaterLock.acquire() #good multithreading practice
				AllLabelsDict["telem"].lastStatus.set(str(argsmessagejson["telem"]))
				AllLabelsDict["telem"].lastTime.set("0")
				StatusClockUpdaterLock.release()
			if "hello" in argsmessagejson and "reply" in argsmessagejson["hello"]:
				OutboundToPlaneOBCInfoLabel.strVar.set("Connected to \'"+str(FromIPaddr)+"\'")
				OutboundToPlaneOBCInfoLabel.MyLabel.config(foreground='#000000')
			print("Status from "+args["from"]+": "+argsmessage)
		else:
			print("Status from MissionDirector (generic): "+str(args))
			if "hello-reply" in args["message"]:
				OutboundToMissionControlInfoLabel.strVar.set("Connected to \'"+str(FromIPaddr)+"\'")
				OutboundToMissionControlInfoLabel.MyLabel.config(foreground='#000000')

StatusClockUpdaterStarted = False
StatusClockUpdaterLock = threading.Lock()
StatusClockUpdaterTimeoutHideTime = 60
StatusClockUpdaterGrayoutTime22 = 40
StatusClockUpdaterGrayoutTime = 20

def ThreadLoopUpdateStatusClocks____():
	StatusClockUpdaterStarted = True
	print("StatusClockUpdater has been started!")
	while True:
		StatusClockUpdaterLock.acquire()
		for key in AllLabelsDict:
			UpdateAClockVar(AllLabelsDict[key])
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
		ListenerToMissionControlInfoLabel.strVar.set("Listening using \'"+str(ipaddr)+"\'")
		ListenerToMissionControlInfoLabel.MyLabel.config(foreground='#000000')

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

def TryConvertStringFromJSON(givenstring):
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
	args = TryConvertStringFromJSON(missionDirectorVarARG.get())
	if len(cmd) == 0:
		print"Please enter command / args"
	else:
		mdmsg = {}
		mdmsg["cmd"] = cmd
		mdmsg["args"] = args
		send_message_to_client(json.dumps(mdmsg), ports.listenport_HumanOperator, mDIPAVar.get())

def planeOBCIPConnect():
	remotemsg = {"cmd":"status", "args":{"hello":"ask"}}
	fwdmsg = {"cmd":"planeobc:"}
	fwdmsg["args"] = {"message":json.dumps(remotemsg),"ip":planeOBCIPVar.get()}
	send_message_to_client(json.dumps(fwdmsg), ports.listenport_HumanOperator, mDIPAVar.get())

def planeOBCSend():
	cmd = planeOBCVarCMD.get()
	args = TryConvertStringFromJSON(planeOBCVarARG.get())
	if len(cmd) == 0:
		print"Please enter command / args"
	else:
		remotemsg = {"cmd":cmd, "args":args}
		fwdmsg = {"cmd":"planeobc:"}
		fwdmsg["args"] = {"message":json.dumps(remotemsg),"ip":planeOBCIPVar.get()}
		send_message_to_client(json.dumps(fwdmsg), ports.listenport_HumanOperator, mDIPAVar.get())

def queryDSLRstatusAction():
	remotemsg = {"cmd":"status", "args":{"DSLR":"ask"}}
	fwdmsg = {"cmd":"planeobc:"}
	fwdmsg["args"] = {"message":json.dumps(remotemsg),"ip":planeOBCIPVar.get()}
	send_message_to_client(json.dumps(fwdmsg), ports.listenport_HumanOperator, mDIPAVar.get())

def queryTelemstatusAction():
	remotemsg = {"cmd":"status", "args":{"telem":"ask"}}
	fwdmsg = {"cmd":"planeobc:"}
	fwdmsg["args"] = {"message":json.dumps(remotemsg),"ip":planeOBCIPVar.get()}
	send_message_to_client(json.dumps(fwdmsg), ports.listenport_HumanOperator, mDIPAVar.get())

def arduinoQueryButtonAction():
	remotemsg = {"cmd":"status", "args":{"arduino":"ask"}}
	fwdmsg = {"cmd":"planeobc:"}
	fwdmsg["args"] = {"message":json.dumps(remotemsg),"ip":planeOBCIPVar.get()}
	send_message_to_client(json.dumps(fwdmsg), ports.listenport_HumanOperator, mDIPAVar.get())

def QueryCPUTempButtonAction():
	remotemsg = {"cmd":"status", "args":{"cpu-temp":"ask"}}
	fwdmsg = {"cmd":"planeobc:"}
	fwdmsg["args"] = {"message":json.dumps(remotemsg),"ip":planeOBCIPVar.get()}
	send_message_to_client(json.dumps(fwdmsg), ports.listenport_HumanOperator, mDIPAVar.get())

def QueryCPUFreqButtonAction():
	remotemsg = {"cmd":"status", "args":{"cpu-freq":"ask"}}
	fwdmsg = {"cmd":"planeobc:"}
	fwdmsg["args"] = {"message":json.dumps(remotemsg),"ip":planeOBCIPVar.get()}
	send_message_to_client(json.dumps(fwdmsg), ports.listenport_HumanOperator, mDIPAVar.get())

def LaunchHeimdallButtonAction():
	remotemsg = {"cmd":"start-heimdall", "args":{}}
	fwdmsg = {"cmd":"planeobc:"}
	fwdmsg["args"] = {"message":json.dumps(remotemsg),"ip":planeOBCIPVar.get()}
	send_message_to_client(json.dumps(fwdmsg), ports.listenport_HumanOperator, mDIPAVar.get())

def heimdallIPConnect():
	#todo: update gui when a reply is received?
	remotemsg = {"cmd":"status", "args":{"hello":"ask"}}
	fwdmsg = {"cmd":"heimdall:"}
	fwdmsg["args"] = {"message":json.dumps(remotemsg),"ip":heimdallIPVar.get()}
	send_message_to_client(json.dumps(fwdmsg), ports.listenport_HumanOperator, mDIPAVar.get()) #forward message to Heimdall through the MissionDirector

def heimdallSend():
	cmd = heimdallVarCMD.get()
	args = TryConvertStringFromJSON(heimdallVarARG.get())
	if len(cmd) == 0:
		print"Please enter command / args"
	else:
		remotemsg = {"cmd":cmd, "args":args}
		fwdmsg = {"cmd":"heimdall:"}
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
Label(topframe, text = "System", font = "bold").grid(row = 0, column = 0)
Label(topframe, text = "cmd / status", font = "bold").grid(row = 0, column = 1)
Label(topframe, text = "arg(s) / IP", font = "bold").grid(row = 0, column = 2)

#systemStatus = Label(topframe, text = "Status", width = 15, font = "bold").grid(row = 0, column = StatusCOLUMN)
#System Names
rowiter = 1
Label(topframe, relief = FLAT, text = "My HumanOperator IP", width = 18).grid(row= rowiter, column = 0)
rowiter += 1
Label(topframe, relief = FLAT, text = "MissionControl IP", width = 18).grid(row= rowiter, column = 0)
rowiter += 1
Label(topframe, relief = FLAT, text = "MissionControl", width = 18).grid(row=rowiter, column = 0)
rowiter += 1
Label(topframe, relief = FLAT, text = "PlaneOBC IP", width = 18).grid(row=rowiter, column = 0)
rowiter += 1
Label(topframe, relief = FLAT, text = "PlaneOBC", width = 18).grid(row=rowiter, column = 0)
rowiter += 1
Label(topframe, relief = FLAT, text = "Heimdall IP", width = 18).grid(row=rowiter, column = 0)
rowiter += 1
Label(topframe, relief = FLAT, text = "Heimdall", width = 18).grid(row=rowiter, column = 0)
rowiter += 1
Label(topframe, relief = FLAT, text = "MissonPlanner IP", width = 18).grid(row = rowiter, column = 0)
rowiter += 1
Label(topframe, relief = FLAT, text = "MissionPlanner", width = 18).grid(row = rowiter, column = 0)
rowiter += 1
Label(topframe, relief = FLAT, text = "Interoperability URL", width = 18).grid(row = rowiter, column = 0)
rowiter += 1
Label(topframe, relief = FLAT, text = "Interoperability", width = 18).grid(row = rowiter, column = 0)

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

######Connection Status Labels

ListenerToMissionControlInfoLabel = ConnectionStatusLabel("not started", 1)
OutboundToMissionControlInfoLabel = ConnectionStatusLabel("not connected", 2)
OutboundToPlaneOBCInfoLabel = ConnectionStatusLabel("not connected", 4)

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
Button(middleFrame, text = "Query OB DSLR Status", width = 20, command = queryDSLRstatusAction).grid(row = 13, column = 2)
Button(middleFrame, text = "Query OB Telem. USB", width = 20, command = queryTelemstatusAction).grid(row = 14, column = 2)

#Button(middleFrame, text = "Query OB Gimbal: todo", width = 20, command = arduinoQueryButtonAction).grid(row = 13, column = 2)

Button(middleFrame, text = "Query OB CPU Temperature", width = 20, command = QueryCPUTempButtonAction).grid(row = 12, column = 3)
Button(middleFrame, text = "Query OB CPU Frequency", width = 20, command = QueryCPUFreqButtonAction).grid(row = 13, column = 3)

Button(middleFrame, text = "Launch OBC Heimdall", width = 16, command = LaunchHeimdallButtonAction).grid(row = 14, column = 0)

#==========================================================================================================


root.mainloop(),










