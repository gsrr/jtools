import time
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.settimeout(20)
while True:
    result = sock.connect_ex(('172.17.22.116',22))
    if result == 0:
       print "Port is open"
       break
    else:
       print "Port is not open"
    time.sleep(1)
sock.close()