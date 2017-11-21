import socket
import threading
import sys
import signal
import random
import os

class Server:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = []
    usernames = []

    def __init__(self):
        self.sock.bind(('0.0.0.0', 9998))
        self.sock.listen(1)

    def handler(self, c, a, user):
        while True:
            data = c.recv(1024)
            for connection in self.connections:
                if(connection is not c):
                    connection.send(data)
            if not data:
                print(user.decode('utf-8') + " disconnected")
                self.connections.remove(c);
                c.close();
                break
    def run(self):
        while True:
            c, a = self.sock.accept()
            user = c.recv(1024)
            print(user.decode('utf-8') + " connected")
            self.connections.append(c)
            c.send(bytes(str(len(self.usernames)) + ' connected clients\n' + ', '.join(self.usernames), 'utf-8'))
            cThread = threading.Thread(target=self.handler, args=(c, a, user))
            cThread.daemon = True
            cThread.start()
            self.usernames.append(str(user, 'utf-8'))
class Client:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    user = ""
    def sendMsg(self):
        while True:
            self.sock.send(bytes(self.user + ": " + input(""), 'utf-8'))

    def __init__(self, address):
        self.sock.connect((address, 9998))
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
            print(str(data, 'utf-8'))


def signal_handler(signal, frame):
        print('Good bye!')
        sys.exit(0)

if (len(sys.argv) > 1):
    signal.signal(signal.SIGINT, signal_handler)
    client = Client(sys.argv[1])
else:
    signal.signal(signal.SIGINT, signal_handler)
    os.system("x-terminal-emulator -e /bin/bash")
    server = Server()
    server.run()
