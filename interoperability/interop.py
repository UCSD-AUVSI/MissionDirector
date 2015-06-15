import httplib, urllib, urllib2
import time
import httplib2
from urllib2 import *
import threading
import socket
import thread



class InterOp:

    def __init__(self, url, username, password):
        self.conn = httplib2.Http()
        self.connObs = httplib2.Http()
        self.username = username
        self.password = password
        self.url = url
        self.login_required = 1
        self.server_connect = 0
        self.stop = False
        self.start = 0
        self.active = 0
        self.end = 0
        self.header={"Connection":" keep-alive"}
        self.gps_data = {"latitude":50.1,"longitude":50.1,"altitude_msl":100.0,"uas_heading":22.35}
        self.listener_started = False



    def threadedconnect(self):
        if self.listener_started == False:
            self.listener_started = True
            self.mythread = threading.Thread(target=self.commandLoop)
            self.mythread.daemon = True
            self.mythread.start()

    def login(self):

        params = urllib.urlencode({"username":self.username,"password":self.password})
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        try:
            r,c = self.conn.request(self.url+"/api/login","POST", headers=headers, body=params)
        except socket.error as e:
            return(-400,str(e))
        if r.status == 200:
            print "Logged In"
            if "set-cookie" in r:
                self.header.update({'Cookie': r['set-cookie']})
            if "Cookie" in self.header:
                self.login_required = 0
        return (r.status,c)

    def serverInfo(self):
        try:
            r,c = self.conn.request(self.url+"/api/interop/server_info","GET", headers=self.header)
        except socket.error as e:
            return(-400,str(e))
        if r.status == 200:
            self.server_data = c
        return (r.status,c)

    def getObstacles(self):

        #self.header.update({'Cookie': "123"})
        try:
            r,c = self.connObs.request(self.url+"/api/interop/obstacles","GET", headers=self.header)
        except socket.error as e:
            return(-400,str(e))

        if r.status == 200:
            self.obstacle_data = c
        return (r.status,c)


    def sendGPS(self,start):
        #gps_data = {"latitude":50.1,"longitude":50.1,"altitude_msl":100.0,"uas_heading":22.35}
        gps = self.gps_data.copy()
        params = urllib.urlencode(gps)
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        headers.update(self.header)

        try:
            r,c = self.conn.request(self.url+"/api/interop/uas_telemetry","POST", headers=headers, body=params)
        except socket.error as e:
            return(-400,str(e))

        return (r.status,c)


    def doLogin(self):
        count = 0
        while self.login_required == 1:
            count+=1
            login,c = self.login()
            if self.stop == True:
                return
            if self.login_required==0:
                serverd,mssg = self.serverInfo()
                if serverd == 400:
                    print "Get Obstacles: "+str(serverd)+": "+mssg
                    self.login_required = 1
                    self.doLogin()
                return True
            else:
                print "Interop server login: "+str(login)+str(c)+str(count)
                time.sleep(1)

    def commandLoop(self):
        # login
        # STAGES
        try:
            self.doLogin()

            # we are logged in
            self.gpsThread = threading.Thread(target=self.doSendGPS)
            self.gpsThread.start()

            self.obstacleThread = threading.Thread(target=self.doGetObstacles)
            self.obstacleThread.start()
            while True:
                if self.login_required == 1:
                    print "Login needed"
                    time.sleep(5)
                    self.commandLoop()
                    break
                time.sleep(.1)
        except KeyboardInterrupt:
            self.stop = True

    def thread_loop(self):
        while True:
            if self.start == 1:
                self.commandLoop()
                self.start = 0
                self.active = 1
            if self.end == 1:
                self.stop = True
                self.end = 0
                self.active = 0
            time.sleep(.5)

    def start_interop(self):
        if self.active == 0:
            self.start = 1
    def end_interop(self):
        if self.active == 1:
            self.end = 1

    def update_gps(self, gps):
        self.gps_data = gps

    def doSendGPS(self):
        print "SendGPS Thread start"
        start = time.time()
        lastsplit = start
        count = 0
        while True:
            if self.login_required == 1 or self.stop == True:
                print "SendGPS Thread end"
                return

            code, mssg = self.sendGPS(time.time())

            if code == 400 or code == -400:
                print "restart"
                if self.login_required == 0:
                    self.login_required = 1
                print "SendGPS Thread end"
                return

            count = count +1
            #time.sleep(.03)
            if count%100 == 0:
                curr = time.time()
                split = curr - lastsplit
                lastsplit = curr
                print "iteration: "+str(count)+" split: "+str(curr-start) +" pcall: "+str(split/10)

    def doGetObstacles(self):
        count = 0
        print "GetObstacles Thread start"
        while True:
            if self.login_required == 1 or self.stop == True:
                print "GetObstacles Thread end"
                return
            code, mssg = self.getObstacles()
            if code == 400 or code == -400:
                print "restart"
                if self.login_required == 0:
                    self.login_required = 1
                print "GetObstacles Thread end"
                return


            count = count +1
            if count%10 == 0:
                print "gotObstacles: "+str(count)
            time.sleep(.2)
