__author__ = 'mysterylz'
import time
import socket
import serial
import Functions
import ClientThread


class Readers:

    #Property
    _readerID = "R001"
    _baud = 9600
    _dataBit = 8
    _port = ''
    _serialPort = serial.Serial()
    _issetSerial = 0
    _MSBORLSB = 0  # MSB = 0, LSB = 1
    _packettype = 0

    #Packet Types
    SINGLEPACKET = 1
    MULTIPACKETS = 2
    #Add new card flag
    _AddError = 0
    _StopAdding = "n"

    #Type of Readers
    _DF760MSB = 0
    _DF760LSB = 1

    #Level of authentication
    _PASSWORD = 0
    _CARD = 1
    _CARDANDPASSWORD = 2

    #Lenght of password and Card ID
    _PASSWORDLEN = 6
    _CARDLEN = 12

    #Server details
    _TCP_IP = "127.0.0.1"
    _TCP_PORT = 23
    _TIMEOUT = 10
    _DATABACK = ""
    clientsocket = ClientThread.socket_client(_readerID, _TCP_IP, _TCP_PORT, _TIMEOUT)

    def getPort(self):
        return self._serialPort.name

    def setPort(self, port):
        try:
            if self.SetSerialPort(port, self._baud, self._dataBit):
                return True
        except:
            return False

    def getBaudrate(self):
        return self._serialPort.baudrate

    def setBaudrate(self, baud):
        try:
            if self.SetSerialPort(self._port, baud, self._dataBit):
                return True
        except:
            return False

    def getDatabit(self):
        return self._serialPort.bytesize

    def setDatabit(self, databit):
        try:
            if self.SetSerialPort(self._port, self._baud, databit):
                return True
        except:
            return False

    def getPasswordLen(self):
        return self._PASSWORDLEN

    def setPasswordLen(self, lens):
        self._PASSWORDLEN = lens

    def getCardIDLen(self):
        return self._CARDLEN

    def setCardIDLen(self, lens):
        self._CARDLEN = lens

    def SetSerialPort(self, port, baud, databit):
        endlessLoop = True
        while endlessLoop:
            try:
                if self._issetSerial == 1:
                    self._serialPort.close()

                self._serialPort.port = port
                self._serialPort.baudrate = baud
                self._serialPort.bytesize = databit
                self._serialPort.parity = serial.PARITY_NONE
                self._serialPort.stopbits = serial.STOPBITS_ONE
                self._serialPort.timeout = None
                self._serialPort.xonxoff = False
                self._serialPort.writeTimeout = None
                self._serialPort.rtscts = False
                self._serialPort.dsrdtr = False
                self._serialPort.interCharTimeout = None

                self._serialPort.close()
                #_serialPort.open()
                self._issetSerial = 1
                self.SaveSettingToFile()
                return True
            except serial.SerialException:
                endlessLoop = True
                self._issetSerial = 0

    def SettingServer(self, serverip, serverport, timeout):
        try:
            #self.clientsocket.client.close()
            self._TCP_IP = serverip
            self._TCP_PORT = serverport
            self._TIMEOUT = timeout
            self.SaveSettingToFile()
            return True
        except:
            return False

    def StartServer(self):
        try:
            self.clientsocket.start()
            while not self.clientsocket.connect:
                time.sleep(0.1)
            return True
        except:
            return False

    def SettingReader(self, readerid, readerType, port, baud, databit, packettype):
        try:
            self._readerID = readerid
            self._packettype = packettype

            if readerType == self._DF760MSB:
                self._MSBORLSB = self._DF760MSB
            elif readerType == self._DF760LSB:
                self._MSBORLSB = self._DF760LSB
            else:
                self._MSBORLSB = self._DF760MSB

            flag = self.SetSerialPort(port, baud, databit)
            if not flag:
                return False
            self.SaveSettingToFile()
            return True
        except:
            return False

    def GetConfiguretion(self, types=0):
        if types == 0:
            config = "{0}:{1}:{2}:{3}:{4}:{5}:{6}".format(self._readerID, self._MSBORLSB, self._port,
                                                              self._dataBit, self._TCP_IP, self._TCP_PORT,self._TIMEOUT)
            return config
        elif types == 1:
            config = "{0}:{1}:{2}:{3}".format(self._readerID, self._MSBORLSB, self._port, self._dataBit)
            return config
        elif types == 2:
            config = "{0}:{1}:{2}".format(self._TCP_IP, self._TCP_PORT, self._TIMEOUT)
            return config

    def OpenPort(self):
        try:
            self._serialPort.open()
            return True
        except serial.SerialException:
            return False

    def ClosePort(self):
        try:
            self._serialPort.close()
            return True
        except serial.SerialException:
            return False

    def PortIsOn(self):
        return self._serialPort.isOpen()

    def ReadData(self, times=0):
        size = 0

        if not (self._serialPort.isOpen()):
            self._serialPort.open()

        while(self._serialPort.isOpen()):
            if times == 0:
                size = self._serialPort.inWaiting()
                if(size != 0):
                    data = self._serialPort.read(size)
                    size = 0
                    return data
                else:
                    size = 0
            else:
                #print "Debug Level 2-2-1"
                start = time.time()
                timeOut = False
                while (size == 0 and timeOut == False):
                    #print "Debug Level 2-2-2"
                    size = self._serialPort.inWaiting()
                    if time.time() > (start+times):
                        timeOut = True
                if timeOut:
                    #print "Debug Level 2-2-2-1"
                    return False
                else:
                    #print "Debug Level 2-2-3"
                    data = self._serialPort.read(size)
                    return data

    def CheckData(self, data, types):
        #Set Database's link
        # db = {'1E4B9A566404': '123456', '1E4B9A566B04': '876543'}

        # Clear buffer for receive new data from server
        self.clientsocket.MESSAGE = ""
        print "Send to Server "

        # Connection flag
        connectErr = False
        if self.clientsocket.SendDataToServer(self._readerID, data, types) == 5:
            self.clientsocket.settingflag = True
            connectErr = True

        # Waiting data from server
        while len(self.clientsocket.MESSAGE) < 1 and not connectErr:
            time.sleep(0.5)

        # Check data from server
        if len(self.clientsocket.MESSAGE) > 1:
            datachecked = self.CheckPacket(self.clientsocket.MESSAGE)
            if datachecked:
                return True
            else:
                return False
        else:
            return False
        
    def CheckPacket(self, data):
        data = str(data)
        checkReaderID = data.find(self._readerID, 0, len(data))
        if checkReaderID < 0:
            return False
        else:
            if data.find("A", 0, len(data)) >= 0:
                tmp = data[data.find("A", 0, len(data))+1]
                if tmp == "1":
                    return True
                else:
                    return False

    def IsPassword(self, data):
        data = data[:-1]
        data = str(data)
        return data.isdigit()

    def StartReader(self, level):

        if self._MSBORLSB == self._DF760LSB:
            return self.DF760KLsb(level)
        elif self._MSBORLSB == self._DF760MSB:
            return self.DF760KMsb(level)

    def SendDataToServer(self, data, types=0):
        typeOfDataErr = 0
        socketNotCreate = 1
        timeOut = 2
        ipNotResolve = 3
        canNotConnectToHost = 4
        sendError = 5
        tmp_IP = ""

        #__Packet creating
        if types == 0:
            Message = "/{0}/C{1}/".format(self._readerID, data)
        elif types == 1:
            Message = "/{0}/P{1}/".format(self._readerID, data)
        else:
            return typeOfDataErr

        #__Socket creating
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            return socketNotCreate

        #__Server connecting
        try:
            tmp_IP = socket.gethostbyname(self._TCP_IP)
        except socket.gaierror:
            return ipNotResolve

        #__Socket connecting
        try:
            sock.connect((self._TCP_IP, self._TCP_PORT))
        except:
            return canNotConnectToHost

        #__Packet sending
        try:
            sock.sendall(Message)
            dataBack = sock.recv(1024)
            self._DATABACK = dataBack
            self._StopAdding = dataBack
        except socket.error:
            return sendError
        finally:
            sock.close()

        return True

    def RecieveDataFromServer(self):
        socketNotCreate = 1
        timeOut = 2
        ipNotResolve = 3
        canNotConnectToHost = 4
        sendError = 5
        tmp_IP = ""
        dataBack = ""

        #__Create socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self._TIMEOUT)
        except socket.error:
            return socketNotCreate

        #__Server checking
        try:
            tmp_IP = socket.gethostbyname(self._TCP_IP)
        except socket.gaierror:
            return ipNotResolve

        #__Server connecting
        try:
            sock.connect((self._TCP_IP, self._TCP_PORT))
        except:
            return canNotConnectToHost

        #__Recieving data
        try:
            dataBack = sock.recv(1024)
        except socket.timeout:
            return timeOut

        sock.close()
        return dataBack

    def AddNewCard(self, amount=0):
        count = 0
        if self._MSBORLSB == 0:
            if amount != 0:
                while count < amount:
                    data = self.ReadData()
                    if not self.IsPassword(data):
                        data = Functions.deleteunusedata(self._CARDLEN, data, self._MSBORLSB)
                        if self.SendDataToServer(data):
                            count += 1
                            self._AddError = 0
                        else:
                            self._AddError = 1
                            if count == 0:
                                count = 0
                            else:
                                count -= 1
                    else:
                        return False
                return True
            else:
                while self._StopAdding == "n":
                    data = self.ReadData()
                    if not self.IsPassword(data):
                        data = Functions.deleteunusedata(self._CARDLEN, data, self._MSBORLSB)
                        if self.SendDataToServer(data):
                            self._AddError = 0
                        else:
                            self._AddError = 1
                    else:
                        return False
                    #self._StopAdding = self.RecieveDataFromServer()
                    #print self._StopAdding
                return True
        else:
            if amount != 0:
                while count < amount:
                    data = self.ReadData()
                    if not self.IsPassword(data):
                        data = Functions.deleteunusedata(self._CARDLEN, data, self._MSBORLSB)
                        data = Functions.newdatasequence(data, self._CARDLEN)
                        if self.SendDataToServer(data):
                            count += 1
                            self._AddError = 0
                        else:
                            self._AddError = 1
                            if count == 0:
                                count = 0
                            else:
                                count -= 1
                    else:
                        return False
                return True
            else:
                while self._StopAdding == "n":
                    data = self.ReadData()
                    if not self.IsPassword(data):
                        data = Functions.deleteunusedata(self._CARDLEN, data, self._MSBORLSB)
                        data = Functions.newdatasequence(data, self._CARDLEN)
                        if self.SendDataToServer(data):
                            self._AddError = 0
                        else:
                            self._AddError = 1
                    else:
                        return False
                    #self._StopAdding = self.RecieveDataFromServer()
                return True

    def PackCardPassword(self, card, password):
        data = "C{0}P{1}".format(card, password)
        return data

    #__Reader check data
    def DF760KMsb(self, level=_CARDANDPASSWORD):
        #Error Code
        _connectionErr = 1
        _serialPortErr = 2
        _cardErr = 3
        _passwordErr = 4

        # Change Reader ID
        tmp = str(self.clientsocket.getreaderid())
        if not tmp.find(self._readerID, 0, len(tmp)) >= 0:
            self._readerID = tmp
            self.SaveSettingToFile()

        # print "Reader ID: ", self._readerID
        # Check Reader's connection
        if self._issetSerial != 1:
            return _connectionErr

        try:
            if not (self._serialPort.isOpen()):
                self._serialPort.open()

            # Read data from Reader
            data = self.ReadData()

            # RFID Tag and Password
            if level == self._CARDANDPASSWORD:
                # When Password first
                if self.IsPassword(data):
                    # print "Debug 1-0"
                    if not data.isdigit():
                        data = data[:-1]
                    data = Functions.deleteunusedata(self._PASSWORDLEN, data, 0)
                    # Save password
                    password = data
                    # print "Debug 1-1"
                    # For send card data and card password to server ( 2 time, card data first or card password first)
                    if self._packettype == self.MULTIPACKETS:
                        if self.CheckData(data, self._PASSWORD):
                            data = self.ReadData(10)
                            if not data:
                                return False
                            # Check Card ID or Password
                            if self.IsPassword(data):
                                # It's Password again
                                return _cardErr
                            else:
                                data = Functions.deleteunusedata(self._CARDLEN, data, 0)
                                if len(data) > self._CARDLEN:
                                    data = data[:-1]
                                if self.CheckData(data, self._CARD):
                                    # Log in complete
                                    return True
                                else:
                                    # Login fail
                                    return False
                        else:
                            return _passwordErr
                    # For send card data and card password to server in single time
                    else:
                        data = self.ReadData(10)
                        if not data:
                            return False
                        # Check Card ID or Password
                        if self.IsPassword(data):
                            # It's Password again
                            return _cardErr
                        else:
                            data = Functions.deleteunusedata(self._CARDLEN, data, 0)
                            if len(data) > self._CARDLEN:
                                data = data[:-1]
                            data = self.PackCardPassword(data, password)
                            # print "Card Data: {0} | Debug".format(data)
                            if self.CheckData(data, self._CARDANDPASSWORD):
                                # Log in complete
                                return True
                            else:
                                # Login fail
                                return False
                else:
                    # When Card first
                    data = Functions.deleteunusedata(self._CARDLEN, data, 0)
                    if len(data) > self._CARDLEN:
                        data = data[:-1]
                    card = data
                    # print "Debug 2-1"
                    # print card
                    # print self._serialPort._baudrate

                    # Check Card ID
                    if self._packettype == self.MULTIPACKETS:
                        if self.CheckData(data, self._CARD):
                            data = self.ReadData(10)
                            # time.sleep(1)
                            if not data:
                                return False
                            # Delete over data
                            if not data.isdigit():
                                data = data[:-1]
                            data = Functions.deleteunusedata(self._PASSWORDLEN, data, 0)
                            # print "Debug 2-2"
                            # Check Password or Card ID
                            if self.IsPassword(data):
                                if self.CheckData(data, self._PASSWORD):
                                    #Login complete
                                    return True
                                else:
                                    #Login fail
                                    return False
                            else:
                                # Password incorrect
                                return _passwordErr
                        else:
                            # Invalid Card
                            return _cardErr
                    else:
                        data = self.ReadData(10)
                        # time.sleep(1)
                        if not data:
                            return False
                        # Delete over data
                        if not data.isdigit():
                            data = data[:-1]
                        data = Functions.deleteunusedata(self._PASSWORDLEN, data, 0)
                        print "Debug 2-2"
                        print data
                        # Check Password or Card ID
                        if self.IsPassword(data):
                            data = self.PackCardPassword(card, data)
                            print data
                            if self.CheckData(data, self._CARDANDPASSWORD):
                                # Login complete
                                return True
                            else:
                                # Login fail
                                return False
                        else:
                            # Password incorrect
                            return _passwordErr
            # RFID Tag only
            elif level == self._CARD:
                # Check RFID Tag or not
                if not self.IsPassword(data):
                    data = Functions.deleteunusedata(self._CARDLEN, data, 0)
                    if len(data) > self._CARDLEN:
                        data = data[:-1]
                    # Check RFID Tag ID
                    if self.CheckData(data, self._CARD):
                        return True
                    else:
                        return False
                else:
                    return _cardErr
            # Password Only
            elif level == self._PASSWORD:
                # Check password or not
                if self.IsPassword(data):
                    if not data.isdigit():
                        data = data[:-1]
                    data = Functions.deleteunusedata(self._PASSWORDLEN, data, 0)
                    # Check password
                    if self.CheckData(data, self._PASSWORD):
                        return True
                    else:
                        return False
                else:
                    return _passwordErr

        except serial.SerialException:
            return _serialPortErr

    def DF760KLsb(self, level=_CARDANDPASSWORD):
        # Error Code
        _connectionErr = 1
        _serialPortErr = 2
        _cardErr = 3
        _passwordErr = 4
        _timeOut = 5

        # Change Reader ID
        tmp = str(self.clientsocket.getreaderid())
        if not tmp.find(self._readerID, 0, len(tmp)) >= 0:
            self._readerID = tmp
            self.SaveSettingToFile()

        # Check Reader's connection
        if self._issetSerial != 1:
            return _connectionErr

        try:
            if not (self._serialPort.isOpen()):
                self._serialPort.open()
            data = self.ReadData()
            if level == self._CARDANDPASSWORD:
                # When Password first
                if self.IsPassword(data):
                    if not data.isdigit():
                        data = data[:-1]
                    data = Functions.deleteunusedata(self._PASSWORDLEN, data, 1)
                    #time.sleep(1)
                    data = Functions.newdatasequence(data, self._PASSWORDLEN)
                    password = data
                    if self._packettype == self.MULTIPACKETS:
                        if self.CheckData(data, self._PASSWORD):
                            data = self.ReadData(10)
                            if len(data) > self._PASSWORDLEN or len(data) > self._CARDLEN:
                                data = data[:-1]
                            # Check Card ID or Password
                            if self.IsPassword(data):
                                # It's Password again
                                return _cardErr
                            else:
                                data = Functions.deleteunusedata(self._CARDLEN, data, 1)
                                #time.sleep(1)
                                if len(data) > self._CARDLEN:
                                    data = data[:-1]
                                data = Functions.newdatasequence(data, self._CARDLEN)
                                if self.CheckData(data, self._CARD):
                                    # Log in complete
                                    return True
                                else:
                                    # Login fail
                                    return False
                        else:
                            return _passwordErr
                    else:
                        data = self.ReadData(10)
                        if len(data) > self._PASSWORDLEN or len(data) > self._CARDLEN:
                            data = data[:-1]
                        # Check Card ID or Password
                        if self.IsPassword(data):
                            # It's Password again
                            return _cardErr
                        else:
                            data = Functions.deleteunusedata(self._CARDLEN, data, 1)
                            #time.sleep(1)
                            if len(data) > self._CARDLEN:
                                data = data[:-1]
                            data = Functions.newdatasequence(data, self._CARDLEN)
                            data = self.PackCardPassword(data, password)
                            if self.CheckData(data, self._CARD):
                                # Log in complete
                                return True
                            else:
                                # Login fail
                                return False
                else:
                    # When Card first
                    if len(data) > self._CARDLEN:
                        data = data[:-1]
                    data = Functions.deleteunusedata(self._CARDLEN, data, 1)
                    data = Functions.newdatasequence(data, self._CARDLEN)
                    card = data
                    if self._packettype == self.MULTIPACKETS:
                        # Check Card ID
                        if self.CheckData(data, self._CARD):
                            data = self.ReadData(10)
                            # Check Password or Card ID
                            if self.IsPassword(data):
                                if not data.isdigit():
                                    data = data[:-1]
                                data = Functions.deleteunusedata(self._PASSWORDLEN, data, 1)
                                data = Functions.newdatasequence(data, self._PASSWORDLEN)
                                if self.CheckData(data, self._PASSWORD):
                                    # Login complete
                                    return True
                                else:
                                    # Login fail
                                    return False
                            else:
                                # Password incorrect
                                return _passwordErr
                        else:
                            # Invalid Card
                            return _cardErr
                    else:
                        data = self.ReadData(10)
                        # Check Password or Card ID
                        if self.IsPassword(data):
                            if not data.isdigit():
                                data = data[:-1]
                            data = Functions.deleteunusedata(self._PASSWORDLEN, data, 1)
                            data = Functions.newdatasequence(data, self._PASSWORDLEN)
                            data = self.PackCardPassword(card, data)
                            if self.CheckData(data, self._PASSWORD):
                                # Login complete
                                return True
                            else:
                                # Login fail
                                return False
                        else:
                            # Password incorrect
                            return _passwordErr
            elif level == self._CARD:
                # Check Tag
                if len(data) > self._CARDLEN:
                    data = data[:-1]
                data = Functions.deleteunusedata(self._CARDLEN, data, 1)
                data = Functions.newdatasequence(data, self._CARDLEN)
                if self.CheckData(data, self._CARD):
                    return True
                else:
                    return _cardErr
            elif level == self._PASSWORD:
                # Check Password
                if not data.isdigit():
                    data = data[:-1]
                data = Functions.deleteunusedata(self._PASSWORDLEN, data, 1)
                data = Functions.newdatasequence(data, self._PASSWORDLEN)
                if self.CheckData(data, self._PASSWORD):
                    return True
                else:
                    return _passwordErr

        except serial.SerialException:
            return _serialPortErr

    def SaveSettingToFile(self):
        try:
            files = open("Setting.txt", mode='w')
            files.writelines(self._readerID)
            files.writelines("\n")
            files.writelines(str(self._baud))
            files.writelines("\n")
            files.writelines(str(self._dataBit))
            files.writelines("\n")
            files.writelines(self._TCP_IP)
            files.writelines("\n")
            files.writelines(self._TCP_PORT)
            files.writelines("\n")
            files.writelines(self._TIMEOUT)
            files.writelines("\n")

            if self._MSBORLSB == self._DF760MSB:
                files.writelines("DF760MSB")
            elif self._MSBORLSB == self._DF760LSB:
                files.writelines("DF760LSB")
            files.writelines("\n")

            if self._packettype == self.SINGLEPACKET:
                files.writelines("SINGLEPACKET")
            elif self._packettype == self.MULTIPACKETS:
                files.writelines("MULTIPACKET")
            files.close()
            return True
        except:
            # print "Writing file fail"
            return False
