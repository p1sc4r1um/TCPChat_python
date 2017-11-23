import socket
import threading
import sys
import signal
import random
import os
import subprocess


global port
global verify

class Client:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    user = ""
    def sendMsg(self):
        while True:
            message = input("")
            verify = 0
            if message:
                if message[0] is "*":
                    if str(message[1:]) == self.user:
                        print("u cant chat with yourself")
                        verify = 0
                    else:
                        verify = 1
                    self.sock.send(bytes(str(verify) + self.user + ": " + message, 'utf-8'))
                    b = self.sock.recv(1024)
                    if(str(b, 'utf-8') == '1'):
                        print('allah uh akbar')
                        os.system("gnome-terminal")

                else:
                    self.sock.send(bytes(str(verify) + self.user + ": " + message, 'utf-8'))


    def __init__(self, address):
        self.sock.connect((address, port))
        print("connected\n")
        self.user = input("username: ")


        self.sock.send(bytes(self.user, 'utf-8'))
        iThread = threading.Thread(target = self.sendMsg)
        iThread.daemon = True
        iThread.start()
        while True:
            data = self.sock.recv(1024)
            if not data:
                break
            else:
                print(str(data, 'utf-8')[1:])

def signal_handler(signal, frame):
    print('Good bye!')
    sys.exit(0)




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
