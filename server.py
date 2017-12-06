import socket
import threading
import sys
import signal
import random
import os
import subprocess
import datetime

global port
global verify
global user_connection
user_connection = []

####BUGS: users shouldn't have ":", "@", "*", " "; groups dont include self person  #####
#TODO: timed messages, write in file, block users
class Server:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = []
    active_usernames = []
    all_usernames = []
    groups = {}
    blocked_users = {}
    #log_file = open("log_file.txt", "a")

    def __init__(self):
        self.sock.bind(('0.0.0.0', 0))
        self.sock.listen(1)
        self.all_usernames = open("users.txt", "r").read().split("\n")
        self.all_usernames.remove("")
        for i in self.all_usernames:
            self.blocked_users[i] = []
        #ir buscar usernames ao ficheiro (aqui ou no run??)
    def handler(self, c, a, user):
        while True:
            data = c.recv(1024)

            if data:
                data_str = str(data, 'utf-8')
                after_dot = data_str[data_str.index(":")+2:]
     #           self.log_file.write("CARALHO")
                print(data_str)
                open("log_file.txt", "a").write(data_str + " at " +str(datetime.datetime.now()) +"\n")
                verify = data_str[0]
                verify_user = 0
                print("after dot: " + str(after_dot))
                if (after_dot[0] == "*") and (len(after_dot) > 1) and (',' in after_dot):
                    group_name = after_dot[after_dot.index('->')+3:]
                    after_dot = after_dot[1:after_dot.index('->')-1].split(",")
                #for user in self.active_usernames:
                    if verify == '1':
                        wanted_connections = []
                        for name in after_dot:
                            for current in self.all_usernames:
                                if current == name:
                                    wanted_connections.append(current)
                                    verify_user = 1
                                    break
                        if verify_user == 0:
                            c.send(bytes('0', 'utf-8'))
                        else:
                            for current in user_connection:
                                if current == user:
                                    wanted_connections.append(current)
                                    verify_user = 1
                                    break
                            self.groups[group_name] = wanted_connections
                            self.groups[group_name].append(user)
                            print(self.groups)
                elif (after_dot[0] == "*") and (len(after_dot) > 1) and (',' not in after_dot):
                    group_name2 = after_dot[1:after_dot.index(" ")]
                    if(group_name2 in self.groups.keys()) and (user in self.groups[group_name2]):
                        message2 = after_dot[after_dot.index(" ")+1:]
                        cThread = threading.Thread(target=self.generatePrivateChat, args = (group_name2,message2, c, user))
                        cThread.daemon = True
                        cThread.start()
                    else:
                        c.send(bytes(" Group doesn't exist", "utf-8"))
                elif after_dot[0] is "@" and len(after_dot) == 1:
                    c.send(bytes(" " + str(self.active_usernames), 'utf-8'))

                elif after_dot[0] is "@" and len(after_dot) > 1 and (' ' in after_dot):
                    '''for user in self.active_usernames:

                        if str(after_dot[1:after_dot.index(" ")]) == str(user) and verify == '1':
                            pritnf("user:")
                            print(after_dot[1:after_dot.index(" ")])
                            #c.send(bytes('1', 'utf-8'))
                            self.connections[self.active_usernames.index(user)].send(bytes(data(:data.index(":")) + after_dot[after_dot.index(" "):], 'utf-8'))
                            #verify_user = 1
                            break

                    #if verify_user == 0:
                        #c.send(bytes('0', 'utf-8'))'''
                    if(user not in self.blocked_users[after_dot[1:after_dot.index(" ")]] and after_dot[1:after_dot.index(" ")] not in self.blocked_users[user]):
                        cThread = threading.Thread(target=self.dialogue, args = (data_str,after_dot))
                        cThread.daemon = True
                        cThread.start()
                    else:
                        c.send(bytes(" blocked!", 'utf-8'))

                elif after_dot[0] is "@" and len(after_dot) > 1 and(' ' not in after_dot):
                    c.send(bytes(" [hint] correct usage: @<user> <message> // @ to view users", "utf-8"))

                elif after_dot[:5] == "!help":
                    c.send(bytes(" private chat: \n\t@<user> <message> // @ to see users\nprivate group: \n\tCREATE: *<user1>,<user2>,...<usern> -> <group_name> \n\tSEND MESSAGE: *<group_name> <message>\n\tADD USER: +<user> <group_name>\n\tREMOVE USER: -<user> <group_name>\nBANNING: ~<user_to_ban> to ban user and ~ again to unban\n","utf-8"))
                elif after_dot[0] is "+":
                    if (after_dot.count(" ") == 1) and (after_dot[1:after_dot.index(" ")] in self.all_usernames) and (after_dot[after_dot.index(" ")+1:] in self.groups.keys()):
                        if after_dot[1:after_dot.index(" ")] not in self.groups[after_dot[after_dot.index(" ")+1:]] and after_dot[1:after_dot.index(" ")] in self.all_usernames:
                            if user in self.groups[after_dot[after_dot.index(" ")+1:]]:
                                self.groups[after_dot[after_dot.index(" ")+1:]].append(after_dot[1:after_dot.index(" ")])
                            else:
                                c.send(bytes(" group doesn't exist","utf-8"))
                        else:
                            c.send(bytes("user already in group", 'utf-8'))
                    elif (after_dot.count(" ") == 0) and after_dot[1:] in self.groups.keys():
                        c.send(bytes(" " + str(self.groups[after_dot[1:]]), 'utf-8'))
                    else:
                        c.send(bytes(" group doesn't exist","utf-8"))
                elif after_dot[0] is "-":
                    if (after_dot.count(" ") == 1) and (after_dot[1:after_dot.index(" ")] in self.all_usernames) and (after_dot[after_dot.index(" ")+1:] in self.groups.keys()):
                        if after_dot[1:after_dot.index(" ")] in self.groups[after_dot[after_dot.index(" ")+1:]] and after_dot[1:after_dot.index(" ")] in self.all_usernames:
                            if user in self.groups[after_dot[after_dot.index(" ")+1:]]:
                                self.groups[after_dot[after_dot.index(" ")+1:]].remove(after_dot[1:after_dot.index(" ")])
                            else:
                                c.send(bytes(" group doesn't exist","utf-8"))
                        else:
                            c.send(bytes(" group doesn't exist", 'utf-8'))
                    elif (after_dot.count(" ") == 0) and after_dot[1:] in self.groups.keys():
                        c.send(bytes(" " + str(self.groups[after_dot[1:]]), 'utf-8'))
                    else:
                        c.send(bytes(" group doesn't exist","utf-8"))

                elif after_dot[0] is "~":
                    if len(after_dot) > 1 and after_dot[1:] in self.all_usernames:
                        if after_dot[1:] not in self.blocked_users[user]:
                            self.blocked_users[user].append(after_dot[1:])
                        else:
                            self.blocked_users[user].remove(after_dot[1:])
                    else:
                        c.send(bytes(" "+str(self.blocked_users[user]), "utf-8"))
                else:
                    for connection in self.connections:
                        #change to inactive too && see if user that sends is blocked in other users
                        if(connection is not c and self.active_usernames[self.connections.index(connection)] not in self.blocked_users[user]) and user not in self.blocked_users[self.active_usernames[self.connections.index(connection)]]:
                            connection.send(bytes(" [GLOBAL] " + data_str[1:], "utf-8"))
            else:
                print(user + " disconnected")
                self.active_usernames.remove(self.active_usernames[self.connections.index(c)])
                self.connections.remove(c);
                c.close();
                break

    def run(self):
        while True:
            c, a = self.sock.accept()
            user = c.recv(1024).decode('utf-8')
            file_users = open("users.txt","r").read()
            s = file_users.replace(",","\n").split("\n")
            if user in s:
                c.send(bytes(" welcome back, "+ user +"!!\n",'utf-8'))
                print(user + " connected")
                #update user while he was gone

            else:
                c.send(bytes(" welcome to IRCHAT, "+ user +"!!\n",'utf-8'))
                open("users.txt","a").write(user+"\n")
                print(user + " connected and added to database")

            self.connections.append(c)
            c.send(bytes(" "+ str(len(self.active_usernames)) + ' connected clients: ' + ', '.join(self.active_usernames) +'\n', 'utf-8'))
            cThread = threading.Thread(target=self.handler, args=(c, a, user))
            cThread.daemon = True
            cThread.start()
            self.active_usernames.append(user)
            self.all_usernames.append(user)
            self.blocked_users[user] = []

    def generatePrivateChat(self, group_name2, message2, c, user):
        #user_connection[0][1].send(bytes(" ola","utf-8"))
        for connection in self.connections:
            if self.active_usernames[self.connections.index(connection)] in self.groups[group_name2]:
                if connection is not c:
                    connection.send(bytes(" "+ user + " to " + str(group_name2) +" -> " + message2,"utf-8"))

    def dialogue(self, message2, after_dot):
            for user in self.active_usernames:

                if str(after_dot[1:after_dot.index(" ")]) == str(user):
                    self.connections[self.active_usernames.index(user)].send(bytes(message2[:message2.index(":")+2]+ after_dot[after_dot.index(" "):], 'utf-8'))
                    #verify_user = 1
                    break

def signal_handler(signal, frame):
        print('Good bye!')
        #self.log_file.close()
        #file_pairs.close()
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
server = Server()
server.run()
