import socket
import threading
import sys
import signal
import random
import os
import subprocess

global port
global verify


####BUGS: users shouldn't have ":", "*",  #####


class Server:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = []
    usernames = []

    def __init__(self):
        self.sock.bind(('0.0.0.0', 0))
        self.sock.listen(1)

    def handler(self, c, a, user):
        while True:
            data = c.recv(1024)
            print(data)


            data_str = str(data, 'utf-8')
            after_dot = data_str[data_str.index(":")+2:]

            if data:
                verify = data_str[0]
                if after_dot[0] is "*":
                    for user in self.usernames:
                        if str(after_dot[1:]) == str(user[:len(after_dot[1:])]) and verify == '1':
                            c.send(bytes('1', 'utf-8'))
                        else:
                            c.send(bytes('0', 'utf-8'))
                else:
                    for connection in self.connections:
                        if(connection is not c):
                            connection.send(data)
            else:
                print(user + " disconnected")
                self.connections.remove(c);
                c.close();
                break

    def run(self):
        while True:
            c, a = self.sock.accept()

            user = c.recv(1024).decode('utf-8')
            s = open("temp","r").read()
            s = s.split("\n")

            if user in s:
                c.send(bytes(" welcome back, "+ user +"!!\n",'utf-8'))
                print(user + " connected")
            else:
                c.send(bytes(" welcome to IRCHAT, "+ user +"!!\n",'utf-8'))
                open("temp","a").write(user+"\n")
                print(user + " connected and added to database")

            self.connections.append(c)
            c.send(bytes(" "+ str(len(self.usernames)) + ' connected clients: ' + ', '.join(self.usernames) +'\n', 'utf-8'))
            cThread = threading.Thread(target=self.handler, args=(c, a, user))
            cThread.daemon = True
            cThread.start()
            self.usernames.append(user)


def signal_handler(signal, frame):
        print('Good bye!')
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
server = Server()
server.run()
