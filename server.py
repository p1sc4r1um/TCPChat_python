import socket
import threading
import sys
import signal
import random
import os
import subprocess

global port
global verify
global user_connection
user_connection = []

### temporary pass as argument (generate private chat)
global wanted_connections
wanted_connections = []

#global group_name
####BUGS: users shouldn't have ":", "*",  #####
#when * only some users work (?????) 

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
            data_str = str(data, 'utf-8')
            after_dot = data_str[data_str.index(":")+2:]

            if data:
                verify = data_str[0]
                verify_user = 0
                if after_dot[0] is "*" and len(after_dot) > 1:
                    global group_name
                    group_name = after_dot[after_dot.index('->')+3:]
                    after_dot = after_dot[1:after_dot.index('->')-1].split(",")
                    #for user in self.usernames:
                    print(group_name)
                    if verify == "1":
                        for name in after_dot:
                            #if name == str(user) and verify == '1':
                            #c.send(bytes('1', 'utf-8'))
                             #   verify_user = 1
                            
                            for current in user_connection:
                                if current[0] == name:
                                    wanted_connections.append(current[1])
                                    verify_user = 1
                                    break

                    if verify_user == 1:
                        cThread = threading.Thread(target=self.generatePrivateChat)
                        cThread.daemon = True
                        cThread.start()

                    elif verify_user == 0:
                        c.send(bytes('0', 'utf-8'))
                elif after_dot[0] is "*" and len(after_dot) == 1:
                    c.send(bytes(str(self.usernames), 'utf-8'))
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
            pair = []
            pair.append(user)
            pair.append(c)
            file_pairs = open("temp","r").read()
            s = file_pairs.replace(",","\n").split("\n")
            user_connection.append(pair)
            if user in s:
                c.send(bytes(" welcome back, "+ user +"!!\n",'utf-8'))
                print(user + " connected")
                        
            else:
                c.send(bytes(" welcome to IRCHAT, "+ user +"!!\n",'utf-8'))
                #open("temp","a").write(pair_user_a+"\n")
                print(user + " connected and added to database")

            self.connections.append(c)
            c.send(bytes(" "+ str(len(self.usernames)) + ' connected clients: ' + ', '.join(self.usernames) +'\n', 'utf-8'))
            cThread = threading.Thread(target=self.handler, args=(c, a, user))
            cThread.daemon = True
            cThread.start()
            self.usernames.append(user)
    
    def generatePrivateChat(self):
        #user_connection[0][1].send(bytes(" ola","utf-8"))
        for connection in wanted_connections:
            connection.send(bytes(" "+str(group_name) +" -> ola","utf-8"))


def signal_handler(signal, frame):
        print('Good bye!')
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
server = Server()
server.run()
