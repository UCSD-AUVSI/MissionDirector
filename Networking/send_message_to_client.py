import socket, threading
import json


def send_message_to_client(msg, port, IPaddr):
	
	# Use this to dispatch the message to another thread so the main thread can't freeze
	# thread = threading.Thread(target=private___dispatch_msg, args=(msg))
	# thread.daemon = True
	# thread.start()
	
	try:
		# Send message using the main thread (TCP may cause a freeze if connection is bad)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((IPaddr,port))
		s.send(msg)
		s.close()
	except:
		print("unable to send message to IP \""+IPaddr+"\" at port "+str(port))



#--------------------------------------------------------------------------------------
# Use this to dispatch the message to another thread so the main thread can't freeze
#
def private___dispatch_msg(msg, port, IPaddr="localhost"):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((IPaddr,port))
	s.send(msg)
	s.close()
