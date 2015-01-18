__author__ = 'mysterylz'
# import pymssql

from readerClass import*
from ClientThread import*
# from Functions import*
import fileinput
#from serial.tools import list_ports


#--------------Init Property------------------#
reader = Readers()
settingList = list()
readerType = ""
readerPacket = ""
try:
    for line in fileinput.FileInput("Setting.txt", mode='r'):
        settingList.append(line)
        if str(line).find("DF760MSB", 0, len(str(line))) >= 0:
            readerType = reader._DF760MSB
            # print "Reader Type: {0}".format(readerType)
        elif str(line).find("DF760LSB", 0, len(str(line))) >= 0:
            readerType = reader._DF760LSB
        else:
            readerType = reader._DF760MSB

        if str(line).find("SINGLEPACKET", 0, len(str(line))) >= 0:
            readerPacket = reader.SINGLEPACKET
            # print "Reader Packet: {0}".format(readerPacket)
        elif str(line).find("MULTIPACKET", 0, len(str(line))) >= 0:
            readerPacket = reader.MULTIPACKETS
        else:
           readerPacket = reader.SINGLEPACKET

    ReaderName = str(settingList[0]).rstrip()
    baud = int(settingList[1])
    databit = int(settingList[2])

    # Server IP & PORT
    HOST = str(settingList[3]).rstrip()
    PORT = int(settingList[4])
    TIMEOUT = int(settingList[5])
    # print "HOST: {0} POST: {1}".format(HOST, PORT)

except:
    # Set to default
    ReaderName = "R001"
    baud = 19200
    databit = 8
    HOST = "10.50.61.54"
    PORT = 43
    TIMEOUT = 10

# print list(list_ports.comports())
# print auto_detect_serial_unix()

# port = "/dev/ttyUSB1"
serialport = auto_detect_serial_unix()
serialport = 'COM3'
# reader.clientsocket.setting(ReaderName, HOST, PORT, TIMEOUT)
reader.SettingServer(HOST, PORT, TIMEOUT)
#--------------End Init Property------------------#


count = 0
print "Searching serial port"
while serialport == "":
    serialport = auto_detect_serial_unix()

print "Setting Reader"
while not reader.SettingReader(ReaderName, readerType, serialport, baud, databit, readerPacket):
    count += 1
count = 0
print "Setting Reader OK"
time.sleep(0.1)
print "Connecting to Reader"
while not reader.OpenPort():
    count += 1
count = 0
print "Reader connected"
time.sleep(0.1)
print "Connecting to Server"
# print "Host IP: {0} Port: {1}".format(reader._TCP_IP, reader._TCP_PORT)
while not reader.StartServer():
    count += 1
count = 0
print "Server connected"
# print "Host IP: {0} Host Port: {1}".format(reader.clientsocket.TCP_IP, reader.clientsocket.TCP_PORT)
time.sleep(0.1)
print "Ready.."
reader.SaveSettingToFile()

while True:
    check = reader.StartReader(reader._CARDANDPASSWORD)
    if check == True:
        print "Open the door"
        check = ""
        print "Ready.."
    elif check == False:
        print "Doesn't Open The Door"
        check = ""
        print "Ready.."
    elif check == 2:
        print "Reader disconnect"
        check = ""

reader.ClosePort()
