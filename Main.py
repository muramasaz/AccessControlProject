__author__ = 'mysterylz'
# import pymssql

from readerClass import*
from ClientThread import*
from Functions import*
#from serial.tools import list_ports



# print list(list_ports.comports())
# print auto_detect_serial_unix()
# Reader
# port = "/dev/ttyUSB1"
serialport = auto_detect_serial_unix()
baud = 19200
databit = 8

print serialport
# Server IP & PORT
HOST = "10.50.41.81"
PORT = 43
ReaderName = "R001"
TIMEOUT = 10
#door = KMtronicWebRelay(link, user, password)
reader = Readers()
reader.clientsocket.setting(ReaderName, HOST, PORT, TIMEOUT)

count = 0
print "Searching serial port"
while serialport == "":
    serialport = auto_detect_serial_unix()

print "Setting Reader"
while not reader.SettingReader('R001', reader._DF760MSB, serialport, baud, databit, reader.SINGLEPACKET):
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
while not reader.StartServer():
    count += 1
count = 0
print "Server connected"
# print "Host IP: {0} Host Port: {1}".format(reader.clientsocket.TCP_IP, reader.clientsocket.TCP_PORT)
time.sleep(0.1)
print "Ready.."

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
