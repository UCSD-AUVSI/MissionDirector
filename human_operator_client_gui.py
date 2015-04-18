from Networking.send_message_to_client import send_message_to_client
from Networking import ports
import json
from Tkinter import *

master = Tk()

def startImaging():
	remotemsg = {}
	remotemsg["command"] = "imaging"
	remotemsg["args"] = {"do":"start"}
	
	fwdmsg = {}
	fwdmsg["command"] = "planeobc:"
	fwdmsg["args"] = {"message":json.dumps(remotemsg),"ip":"10.42.0.69"}
	
	send_message_to_client(json.dumps(fwdmsg), ports.listenport_HumanOperator)

def stopImaging():
	remotemsg = {}
	remotemsg["command"] = "imaging"
	remotemsg["args"] = {"do":"stop"}
	
	fwdmsg = {}
	fwdmsg["command"] = "planeobc:"
	fwdmsg["args"] = {"message":json.dumps(remotemsg),"ip":"10.42.0.69"}
	
	send_message_to_client(json.dumps(fwdmsg), ports.listenport_HumanOperator)


bStart = Button(master, text="Start Imaging", width=20, command=startImaging)
bStart.pack()

bStop = Button(master, text="Stop Imaging", width=20, command=stopImaging)
bStop.pack()

mainloop()

