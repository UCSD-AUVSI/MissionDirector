

import interop
url = "http://10.10.130.10:80"
username = "ucsd-auvsi"
password = "1979543783"
connection = interop.InterOp(url, username, password)

#start interop connection
connection.commandLoop()
#start the sending of data
#connection.start_interop()
	
