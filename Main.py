__author__ = 'mysterylz'
# import pymssql
from readerClass import*
from ClientThread import*


# Reader
port = "/dev/ttyUSB1"
baud = 19200
databit = 8

# Server IP & PORT
HOST = "10.50.41.81"
PORT = 43
ReaderName = "R001"
TIMEOUT = 10
#door = KMtronicWebRelay(link, user, password)
reader = Readers()
reader.clientsocket.setting(ReaderName, HOST, PORT, TIMEOUT)

count = 0
print "Setting Reader"
while not reader.SettingReader('R001', reader._DF760MSB, port, baud, databit, reader.SINGLEPACKET):
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