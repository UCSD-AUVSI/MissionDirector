import socket, threading
from Networking import ports
import ssl


def send_message_to_client(msg, port, IPaddr):
	
	# Use this to dispatch the message to another thread so the main thread can't freeze
	thread = threading.Thread(target=private___dispatch_msg, args=(msg,port,IPaddr))
	thread.daemon = True
	thread.start()


#--------------------------------------------------------------------------------------
# Use this to dispatch the message to another thread so the main thread can't freeze
#
def private___dispatch_msg(msg, port, IPaddr):
	try:
		if port == ports.outport_PlaneOBC and IPaddr != "localhost":
			s_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s = ssl.wrap_socket(s_,
						ssl_version=ssl.PROTOCOL_TLSv1,
						cert_reqs=ssl.CERT_REQUIRED,
						ca_certs='/etc/ssl/certs/ucsd-auvsi-cert.crt')
		else:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((IPaddr,port))
		s.send(msg)
		s.close()
	except:
		print("warning: unable to send message to IP \""+IPaddr+"\" at port "+str(port))

