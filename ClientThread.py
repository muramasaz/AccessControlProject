__author__ = 'mysterylz'
import threading
import socket
import sys
import time
import operator
import fileinput


class socket_server(threading.Thread):
    TCP_IP = "127.0.0.1"
    TCP_PORT = 7777
    BUFFER_SIZE = 20
    daemon = True

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.TCP_IP, self.TCP_PORT))
        s.listen(1)

        conn, addr = s.accept()
        (ip, port) = addr

        sys.stdout.write("%s connection address: IP %s on Port %d\n" % (self.__class__.__name__, ip, port))

        data = True
        while data:

            data = conn.recv(self.BUFFER_SIZE)

            if data:
                sys.stdout.write("%s received data: %s\nSend data back:\n" % (self.__class__.__name__, data))
                send_data = raw_input()
                sys.stdout.write("%s sending data: %s\n" % (self.__class__.__name__, send_data))
                conn.send(send_data)
            data = True

        conn.close()


class socket_client(threading.Thread):
    TCP_IP = "127.0.0.1"
    TCP_PORT = 443
    BUFFER_SIZE = 1024
    TIMEOUT = 10.0
    BID = "RFFF"
    ID = "R001"
    MESSAGE = ""
    client = socket.socket()
    connect = False
    disconnect = False
    settingflag = False
    settingcomplete = False
    INITREADERNAME = False

    def __init__(self, rid, ip, port, timeout):
        super(socket_client, self).__init__()
        self.TCP_IP = ip
        self.TCP_PORT = port
        self.TIMEOUT = timeout
        self.ID = rid
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        while not self.connect:
            try:
                self.client.connect((self.TCP_IP, self.TCP_PORT))
                self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                #self.client.settimeout(self.TIMEOUT)
                self.connect = True
                #print "Debug 3\n"
            except socket.error as e:
                #print "Socket Error Code: {0}".format(e.errno)
                self.connect = False

        data = True
        while data:
            try:
                if self.settingflag:
                    try:
                        #self.client.shutdown(socket.SHUT_RDWR)
                        #time.sleep(0.1)
                        self.client.close()
                        clientclose = True
                    except socket.error as e:
			#print "Socket closing fail. Error Code: {0}".format(e.errno)
                        clientclose = False

                    if clientclose:
                        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        #self.client.settimeout(self.TIMEOUT)
                        while self.settingflag:
                            try:
				#print "IP: {0} Port: {1}".format(self.TCP_IP, self.TCP_PORT)
                                self.client.connect((self.TCP_IP, self.TCP_PORT))
                                self.settingflag = False
                                self.settingcomplete = True
                            except socket.error:
				#print "Setting socket fail"
                                self.settingflag = True
                    else:
                        self.settingflag = True

                data = self.client.recv(self.BUFFER_SIZE)
                self.MESSAGE = data
                self.checkcommand(data)
                data = True

            #except socket.timeout:
                #data = True
            except socket.error:
                self.disconnect = True

    def senddata(self, text):
        try:
            self.client.send(str(text))
            return True
        except:
            return False

    def setting(self, rid, ip, port, timeout):
        self.ID = rid
        self.TCP_IP = ip
        self.TCP_PORT = port
        self.TIMEOUT = timeout
        self.settingflag = True

    def SendDataToServer(self, readerID, data, types=0):
        typeOfDataErr = 0
        sendError = 5

        # Packet creating
        if types == 0:
            Message = "#{0}C{1}#".format(readerID, data)
        elif types == 1:
            Message = "#{0}P{1}#".format(readerID, data)
        elif types == 2:
            Message = "#{0}{1}#".format(readerID, data)
        else:
            return typeOfDataErr
        # Packet sending
        try:
            self.client.send(str(Message))
            return True
        except socket.error as e:
            if e.errno == 10054:
                # Server has been offline, try to reconnect
                self.settingflag = True
            return sendError

    def checkcommand(self, data):
        # print "Check command\n"
        data = str(data)
        ip = list()
        port = list()
        timeout = list()
        rid = list()

        #print "Data IN: %s Len: %s" % (data, len(data))
        if data.find(self.ID, 0, len(data)) > 0 or data.find(self.BID, 0, len(data)) > 0:
            # Set new server IP, Port, Timeout
            if data.find("I", 0, len(data)) >= 0 and data.find("N", 0, len(data)) < 0:
                i = data.find("I", 0, len(data)) + 1
                # Save new server port
                while i < data.find("P", 0, len(data)):
                    ip.append(data[i])
                    i += 1
                ip = reduce(operator.add, ip)
                i = data.find("P", 0, len(data)) + 1
                # Save new timeout
                while i < data.find("T", 0, len(data)):
                    port.append(data[i])
                    i += 1
                port = reduce(operator.add, port)
                port = int(port)
                i = data.find("T", 0, len(data)) + 1
                while i < data.find("$", 1, len(data)):
                    timeout.append(data[i])
                    i += 1
                timeout = reduce(operator.add, timeout)
                timeout = int(timeout)
                #print "IP = %s \nPORT = %s \nTIME = %s" % (ip, port, timeout)
                # Set new server IP, Port, Timeout
                self.setting(self.ID, ip, port, timeout)
            # Set new reader ID
            elif data.find("N", 0, len(data)) >= 0:
                i = data.find("N", 0, len(data)) + 1
                # print "i = {0} len = {1} data = {2}".format(i, len(data), data)
                if data.find("I", i-1, len(data)) >= 0:
                    i += 1
                    if not self.INITREADERNAME:
			#print "Set reader ID 1st time"
                        self.INITREADERNAME = True
                        while i < data.find("$", 1, len(data)):
                            rid.append(data[i])
                            i += 1
                        # print(rid)
                        rid = reduce(operator.add, rid)
			if self.checkreaderidfromsettingfile(rid):
	                  self.ID = rid
                else:
		    #print "Set new reader ID"
                    while i < data.find("$", 1, len(data)):
                        rid.append(data[i])
                        i += 1
                    # print(rid)
                    rid = reduce(operator.add, rid)
                    self.ID = rid
           # elif data.find("GR", 0, len(data) >= 0):
		#print "Get reader name"
                #self.SendDataToServer(self.ID, "", 2)
        else:
            # print "Debug Reader not match\n"
            self.MESSAGE = ""
            return False

    def getreaderid(self):
        return self.ID
 
    def checkreaderidfromsettingfile(self, rid):
	settingData = list()
	for line in fileinput.input("Setting.txt", mode="r"):
	    settingData.append(line)
	readerID = str(settingData[0]).rstrip()
	if readerID.find("RFFF", 0) >= 0:
	  return True
        else:
	  return False

