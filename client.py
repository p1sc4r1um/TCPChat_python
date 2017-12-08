import socket
import threading
import sys
import signal
import random
import os
import subprocess
from time import sleep
def cls():
    os.system('reset')

global port
global verify
global mainpid

class Client:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    user = ""
    def sendMsg(self):
        while True:
            message = input("")
            
            verify = 0
            if message:
                if message == "exit":
                    os.kill(mainpid,signal.SIGINT)
                if (message[0] is "@" or message[0] is "*") and len(message) > 1:
                    split = message[1:].split(",")
                    for name in split:
                        if name == self.user and message[0] == "@" and (len(message) > len(name) + 1):
                            print("u cant chat with yourself")
                            verify = 0
                            break
                        else:
                            verify = 1
                self.sock.send(bytes(str(verify) + self.user + ": " + message, 'utf-8'))

    def __init__(self, address):
        self.sock.connect((address, port))
        print("connected\n")
        self.user = input("username: ")
        os.system("reset")

        self.sock.send(bytes(self.user, 'utf-8'))
        iThread = threading.Thread(target = self.sendMsg)
        iThread.daemon = True
        iThread.start()
        while True:
            data = self.sock.recv(1024)
            if not data:
                break
            else:
                if str(data, 'utf-8')[0] == "1":
                    print(str(data, 'utf-8')[1:])

                elif (str(data, 'utf-8')[0] == "0") and len(str(data, 'utf-8')) < 3:
                    print("user doesn't exist")
                elif(str(data, 'utf-8') == "¹@£§½¬{[]}1q2w3e4r5t6y"):
                    cls()

                else:
                    print(str(data, 'utf-8')[1:])

def signal_handler(signal, frame):
    print('Good bye!')
    sys.exit(0)

mainpid = os.getpid()
if (len(sys.argv) == 2):
    try:
        socket.inet_aton(sys.argv[1])
        signal.signal(signal.SIGINT, signal_handler)
        s = str(subprocess.getoutput("lsof -Pn -i4 | grep TCP"))
        port = int(s[s.rfind(":")+1:s.rfind("(")-1])
        client = Client(sys.argv[1])
    except socket.error:
        print("client <address>")
else:
    print("client <address>")
