import socket
import threading
import sys
import signal
import random
import os
import subprocess
import datetime
import glob
import ast
from time import sleep

global port
global verify
global user_connection
user_connection = []

####BUGs:#####
#TODO: timed messages, write in
#group_names cant have same name yeaeyyae
#buguinhos
#exit sends a motherfucking message
#save blocked list
class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Server:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = []
    active_usernames = []
    all_usernames = []
    groups = {}
    blocked_users = {}

    def __init__(self):
        self.sock.bind(('0.0.0.0', 0))
        self.sock.listen(1)
        print("Server initialized")
        if os.path.exists("blocked.txt"):
            if len(open("blocked.txt", "r+").read()) > 10:
                self.blocked_users = ast.literal_eval(open("blocked.txt", "r").read())
        if os.path.exists("groups.txt"):
            if len(open("groups.txt", "r+").read()) > 10:
                self.groups = ast.literal_eval(open("groups.txt", "r").read())
        if os.path.exists("users.txt"):
            self.all_usernames = open("users.txt", "r").read().split("\n")
            self.all_usernames.remove("")
            for i in self.all_usernames:
                self.blocked_users[i] = []
        print("-database uploaded\n")
    def handler(self, c, a, user):
        while True:
            data = c.recv(1024)
            if data:
                data_str = str(data, 'utf-8')
                after_dot = data_str[data_str.index(":")+2:]
                if after_dot[0] != "^":
                    open(user + "_tmp.txt", "a+").write(after_dot + "\n")
                open("log_file.txt", "a+").write(data_str + " at " +str(datetime.datetime.now()) +"\n")
                verify = data_str[0]
                verify_user = 0
                if (after_dot[0] == "*") and (len(after_dot) > 1) and (',' in after_dot) and after_dot.count("->") == 1 and len(after_dot[after_dot.index("->")+3:]) > 2:
                    group_name = after_dot[after_dot.index('->')+3:]
                    after_dot = after_dot[1:after_dot.index('->')-1].split(",")
                    if(group_name not in self.groups.keys()):
                        if verify == '1':
                            wanted_connections = []
                            wanted_connections.append(user)
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
                    else:
                        c.send(bytes(" group already exists", 'utf-8'))
                        open(user+"_tmp.txt", "a+").write("group already exists")
                elif (after_dot[0] == "*") and (len(after_dot) > 1) and after_dot.count("->") == 0 and after_dot.count(" ") != 0 and after_dot.count(",") == 0:
                    group_name2 = after_dot[1:after_dot.index(" ")]
                    if(group_name2 in self.groups.keys()) and (user in self.groups[group_name2]):
                        message2 = after_dot[after_dot.index(" ")+1:]
                        cThread = threading.Thread(target=self.generatePrivateChat, args = (group_name2,message2, c, user))
                        cThread.daemon = True
                        cThread.start()
                    else:
                        c.send(bytes(" group doesn't exist", "utf-8"))
                        open(user+"_tmp.txt", "a+").write("group doesn't exist")
                elif (after_dot[0] == "*") and (after_dot.count("->") != 1 or after_dot.count(" ") != 0):
                    c.send(bytes(" "+ bcolors.RED +"[hint] correct usage: *<user1>,<usern> -> <group_name> // *<group_name> message" + bcolors.ENDC, 'utf-8'))
                    open(user+"_tmp.txt", "a+").write(bcolors.RED +"[hint] correct usage: *<user1>,<usern> -> <group_name> // *<group_name> message" + bcolors.ENDC+"\n")
                elif after_dot[0] is "@" and len(after_dot) == 1:
                    c.send(bytes(" " + str(self.active_usernames), 'utf-8'))
                    open(user+"_tmp.txt", "a+").write(str(self.active_usernames) + "\n")
                elif after_dot[0] is "@" and len(after_dot) > 1 and (' ' in after_dot):
                    u = after_dot[1:after_dot.index(" ")]
                    if u in self.all_usernames:
                        if(user not in self.blocked_users[after_dot[1:after_dot.index(" ")]] and after_dot[1:after_dot.index(" ")] not in self.blocked_users[user]):
                            cThread = threading.Thread(target=self.dialogue, args = (data_str,after_dot))
                            cThread.daemon = True
                            cThread.start()
                        else:
                            c.send(bytes(" blocked!", 'utf-8'))
                            open(user+"_tmp.txt", "a+").write("blocked!\n")
                    else:
                        c.send(bytes(" user doesn't exist", 'utf-8'))
                        open(user+"_tmp.txt", "a+").write("user doesn't exist\n")
                elif after_dot[0] is "@" and len(after_dot) > 1 and (' ' not in after_dot):
                    c.send(bytes(" "+bcolors.RED+"[hint] correct usage: @<user> <message> // @ to view users"+bcolors.ENDC+"\n", "utf-8"))
                    open(user+"_tmp.txt", "a+").write(bcolors.RED+"[hint] correct usage: @<user> <message> // @ to view users"+bcolors.ENDC+"\n\n")

                elif after_dot[:5] == "!help":
                    c.send(bytes(" private chat: \n\t@<user> <message> // @ to see users\nprivate group: \n\tCREATE: *<user1>,<user2>,...<usern> -> <group_name> \n\tSEND MESSAGE: *<group_name> <message>\n\tADD USER: +<user> <group_name>\n\tREMOVE USER: -<user> <group_name>\nbanning users: ~<user_to_ban> to ban user and ~ again to unban\nlist chats: ls to list // ls <chat_name> to see specific chat\ntimed messages: ^<time>@ (or *)<user> (or <groupname>) <message>\nexit the program: type exit\n","utf-8"))
                    open(user+"_tmp.txt", "a+").write("private chat: \n\t@<user> <message> // @ to see users\nprivate group: \n\tCREATE: *<user1>,<user2>,...<usern> -> <group_name> \n\tSEND MESSAGE: *<group_name> <message>\n\tADD USER: +<user> <group_name>\n\tREMOVE USER: -<user> <group_name>\nbanning users: ~<user_to_ban> to ban user and ~ again to unban\nlist chats: ls to list // ls <chat_name> to see specific chat\ntimed messages: ^<time>@ (or *)<user> (or <groupname>) <message>\nexit the program: type exit\n")
                elif after_dot[0] is "+":
                    if (after_dot.count(" ") == 1) and (after_dot[1:after_dot.index(" ")] in self.all_usernames) and (after_dot[after_dot.index(" ")+1:] in self.groups.keys()):
                        if after_dot[1:after_dot.index(" ")] not in self.groups[after_dot[after_dot.index(" ")+1:]] and after_dot[1:after_dot.index(" ")] in self.all_usernames:
                            if user in self.groups[after_dot[after_dot.index(" ")+1:]]:
                                self.groups[after_dot[after_dot.index(" ")+1:]].append(after_dot[1:after_dot.index(" ")])
                                cThread = threading.Thread(target=self.connectedToGroup, args = (after_dot[after_dot.index(" ")+1:],after_dot[1:after_dot.index(" ")],user))
                                cThread.daemon = True
                                cThread.start()
                            else:
                                c.send(bytes(" group doesn't exist","utf-8"))
                                open(user + "_tmp.txt", "a+").write("group doesn't exist\n")

                        else:
                            c.send(bytes(" user already in group", 'utf-8'))
                            open(user+"_tmp.txt", "a+").write("user already in group\n")
                    elif (after_dot.count(" ") == 0) and after_dot[1:] in self.groups.keys():
                        c.send(bytes(" " + str(self.groups[after_dot[1:]]), 'utf-8'))
                        open(user+"_tmp.txt", "a+").write(str(self.groups[after_dot[1:]])+"\n")
                    else:
                        c.send(bytes(" group doesn't exist","utf-8"))
                        open(user + "_tmp.txt", "a+").write("group doesn't exist\n")
                elif after_dot[0] is "-":
                    if (after_dot.count(" ") == 1) and (after_dot[1:after_dot.index(" ")] in self.all_usernames) and (after_dot[after_dot.index(" ")+1:] in self.groups.keys()):
                        if after_dot[1:after_dot.index(" ")] in self.groups[after_dot[after_dot.index(" ")+1:]] and after_dot[1:after_dot.index(" ")] in self.all_usernames:
                            if user is self.groups[after_dot[after_dot.index(" ")+1:]][0]:
                                self.groups[after_dot[after_dot.index(" ")+1:]].remove(after_dot[1:after_dot.index(" ")])
                                cThread = threading.Thread(target=self.removeFromGroup, args = (after_dot[after_dot.index(" ")+1:],after_dot[1:after_dot.index(" ")],user))
                                cThread.daemon = True
                                cThread.start()

                            else:
                                c.send(bytes(" group doesn't exist or you don't have permissions","utf-8"))
                                open(user+"_tmp.txt", "a+").write("group doesn't exist or you don't have permissions\n")
                        else:
                            c.send(bytes(" group doesn't exist", 'utf-8'))
                            open(user+"_tmp.txt", "a+").write("group doesn't exist\n")

                    elif (after_dot.count(" ") == 0) and after_dot[1:] in self.groups.keys():
                        c.send(bytes(" " + str(self.groups[after_dot[1:]]), 'utf-8'))
                        open(user + "_tmp.txt", "a+").write(str(self.groups[after_dot[1:]])+"\n")
                    else:
                        c.send(bytes(" group doesn't exist","utf-8"))
                        open(user+"_tmp.txt", "a+").write("group doesn't exist\n")


                elif after_dot[0] is "~":
                    if len(after_dot) > 1 and after_dot[1:] in self.all_usernames:
                        if after_dot[1:] not in self.blocked_users[user]:
                            self.blocked_users[user].append(after_dot[1:])
                        elif after_dot[1:] in self.blocked_users[user]:
                            self.blocked_users[user].remove(after_dot[1:])
                        else:
                            c.send(bytes(" "+bcolors.RED+"[hint] correct usage: ~<user>\n"+bcolors.ENDC, "utf-8"))
                            open(user+"_tmp.txt", "a+").write(bcolors.RED+"[hint] correct usage: ~<user>\n"+bcolors.ENDC+"\n")
                    else:
                        c.send(bytes(" "+str(self.blocked_users[user]), "utf-8"))
                        open(user + "_tmp.txt", "a+").write(str(self.blocked_users[user]) + "\n")
                elif after_dot == "ls":
                    filenames = glob.glob("/home/IRC/"+user+"/*.txt")
                    names = []
                    for f in filenames:
                        names.append(f[f.index("IRC/")+5+len(user):f.index(".txt")])
                    c.send(bytes(" "+str(names), 'utf-8'))
                    open(user + "_tmp.txt", "a+").write(str(names)+"\n")
                elif after_dot[:2] == "ls" and after_dot.count(" ") == 1 and len(after_dot[3:]) > 0:
                    filenames = glob.glob("/home/IRC/"+user+"/*.txt")
                    names = []
                    for f in filenames:
                        names.append(f[f.index("IRC/")+5+len(user):f.index(".txt")])
                    for n in names:
                        if n == after_dot[3:]:
                            t = open("/home/IRC/"+user+"/"+n+".txt","r").readlines()
                            for line in t:
                                if line != "////@£§£½§¬½{[{[.read until here.\n":
                                    c.send(bytes(" "+str(line), 'utf-8'))
                                    open(user+"_tmp.txt", "a+").write(str(t) + "\n")
                elif after_dot[:2] == "ls" and after_dot.split(" ")[1] == "-n" and len(after_dot.split(" ")) == 3:
                    filenames = glob.glob("/home/IRC/"+user+"/*.txt")
                    names = []
                    boolean = 0
                    for f in filenames:
                        names.append(f[f.index("IRC/")+8:f.index(".txt")])
                    for n in names:
                        if n == after_dot.split(" ")[2]:
                            t = open("/home/IRC/"+user+"/"+n+".txt","r").read()
                            t.split("\n")
                            for i in t:
                                if t == "////@£§£½§¬½{[{[.read until here.":
                                    boolean = 1
                                if boolean == 1:
                                    c.send(bytes(" " + str(i), 'utf-8'))
                                    open(user + "_tmp.txt", "a+").write(str(i)+"\n")
                    f = open("/home/IRC/"+user+"/"+n+".txt","r")
                    lines = f.readlines()
                    f.close()
                    f = open("/home/IRC/"+user+"/"+n+".txt", "w")
                    for line in lines:
                        if line!="////@£§£½§¬½{[{[.read until here.\n":
                            f.write(line)
                    f.close()
                elif after_dot[0] == "^" and after_dot.count(" ") != 0:
                    if after_dot.count("@") == 1:
                        number = int(after_dot[1:after_dot.index("@")])
                        username_timed = after_dot[after_dot.index("@")+1:after_dot.index(" ")]
                        p = []
                        p.append(username_timed)
                        p.append(user)


                    elif after_dot.count("*") == 1:
                        number = int(after_dot[1:after_dot.index("*")])
                        groupname_timed = after_dot[after_dot.index("*")+1:after_dot.index(" ")]
                        p = self.groups[groupname_timed]

                    m = after_dot[after_dot.index(" "):] # tem espaço
                    cThread = threading.Thread(target=self.waitToClean, args=(number, p, user, m))
                    cThread.daemon = True
                    cThread.start()
                elif after_dot == "exit":
                    for connection in self.connections:
                        if connection is not c:
                            connection.send(bytes(" "+ user + " disconnected", 'utf-8'))
                else:
                    for connection in self.connections:
                        #change to inactive too && see if user that sends is blocked in other users
                        if(connection is not c and self.active_usernames[self.connections.index(connection)] not in self.blocked_users[user]) and user not in self.blocked_users[self.active_usernames[self.connections.index(connection)]]:
                            connection.send(bytes(" " + bcolors.BLUE + "[GLOBAL] " + bcolors.ENDC + bcolors.UNDERLINE + data_str[1:len(user)+1] + bcolors.ENDC + data_str[len(user)+1:], "utf-8"))
                            open(self.active_usernames[self.connections.index(connection)] + "_tmp.txt", "a+").write(bcolors.BLUE + "[GLOBAL] " + bcolors.ENDC + bcolors.UNDERLINE + data_str[1:len(user)+1] + bcolors.ENDC + data_str[len(user)+1:] + "\n")
            else:
                filenames = glob.glob("/home/IRC/"+ user +"/*.txt")
                for f in filenames:
                    open(f,"a+").write("////@£§£½§¬½{[{[.read until here.\n")
                open("groups.txt", "w").write(str(self.groups))
                open("blocked.txt", "w").write(str(self.blocked_users))
                print(user + " disconnected")
                os.remove(user+"_tmp.txt")
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
            if user.count(" ") == 0 and user.count("*") == 0 and user.count("@") == 0 and user.count("+") == 0 and user.count("-") == 0 and user.count("~") == 0 and user.count(":") == 0:
                if user not in self.active_usernames:
                    if user in s:
                        c.send(bytes(" welcome back, "+ user +"!!\n",'utf-8'))
                        open(user + "_tmp.txt", "a+").write("welcome back, "+ user +"!!\n\n")
                        print(user + " connected from "+str(a[0])+":"+str(a[1]))
                        filenames = glob.glob("/home/IRC/" + user + "/*.txt")
                        for f in filenames:
                            lines = open(f, "r").readlines()
                            if len(lines) > 0:
                                if lines[len(lines)-1] != "////@£§£½§¬½{[{[.read until here.\n":
                                    c.send(bytes("\n"+bcolors.RED + "you've got new messages in " + bcolors.BOLD +f[f.index(user)+len(user)+1:len(f)-4]+ bcolors.ENDC + bcolors.RED +" [type ls " + f[f.index(user)+len(user)+1:len(f)-4]+" to see]"+bcolors.ENDC+"\n",'utf-8'))
                                    open(user + "_tmp.txt", "a+").write(bcolors.RED + "you've got new messages in " + bcolors.BOLD +f[f.index(user)+len(user)+1:len(f)-4]+ bcolors.ENDC + bcolors.RED +" [type ls " + f[f.index(user)+len(user)+1:len(f)-4]+" to see]"+bcolors.ENDC+"\n\n")

                    else:
                        c.send(bytes(" welcome to IRCHAT, "+ user +"!!\n",'utf-8'))
                        open(user + "_tmp.txt", "a+").write("welcome to IRCHAT, "+ user +"!!\n\n")
                        open("users.txt","a+").write(user+"\n")
                        print(user + " connected and added to database")
                        path = "/home/IRC/"+user+"/"
                        os.makedirs(path)
                        open(path+user+"_GLOBAL.txt","w+")

                    c.send(bytes("\npress "+ bcolors.BOLD +"!help"+ bcolors.ENDC  +" to see the chat's manual\n\n",'utf-8'))
                    open(user+"_tmp.txt", "a+").write("press "+bcolors.BOLD +"!help"+ bcolors.ENDC+ " to see the chat's manual\n\n\n")
                    self.connections.append(c)
                    c.send(bytes(" "+ str(len(self.active_usernames)) + ' connected clients: ' + bcolors.GREEN +', '.join(self.active_usernames)+ bcolors.ENDC +'\n', 'utf-8'))
                    open(user+"_tmp.txt", "a+").write(str(len(self.active_usernames)) + ' connected clients: ' + bcolors.GREEN  + ', '.join(self.active_usernames)+ bcolors.ENDC +'\n\n')
                    for connection in self.connections:
                        if connection is not c:
                            connection.send(bytes(" "+ user +" connected\n", 'utf-8'))
                            open(self.active_usernames[self.connections.index(connection)]+"_tmp.txt", "a+").write(user +" connected\n\n")
                    cThread = threading.Thread(target=self.handler, args=(c, a, user))
                    cThread.daemon = True
                    cThread.start()
                    self.active_usernames.append(user)
                    self.all_usernames.append(user)
                    self.blocked_users[user] = []
                else:
                    c.send(bytes(" user already connected", 'utf-8'))
                    open(user+"_tmp.txt", "a+").write("user already connected\n")
                    c.close()
            else:
                c.send(bytes(" username cannot contain special characters such as ' *@+-~:lsexit'", 'utf-8'))
                open(user+"_tmp.txt", "a+").write("username cannot contain special characters such as ' *@+-~:lsexit'\n")
                c.close()
    def generatePrivateChat(self, group_name2, message2, c, user):
        for connection in self.connections:
            if self.active_usernames[self.connections.index(connection)] in self.groups[group_name2]:
                if connection is not c:
                    connection.send(bytes(" "+ bcolors.BOLD + user + bcolors.ENDC  + " to " + bcolors.GREEN +str(group_name2) + bcolors.ENDC  +" -> " + message2,"utf-8"))
                    open(self.active_usernames[self.connections.index(connection)]+"_tmp.txt", "a+").write(bcolors.BOLD + user + bcolors.ENDC  + " to " + bcolors.GREEN +str(group_name2) + bcolors.ENDC  +" -> " + message2)
        for username in self.all_usernames:
            if username in self.groups[group_name2]:
                if username == user:
                    open("/home/IRC/" + username + "/" + group_name2 + ".txt","a+").write(message2 + "\n")
                else:
                    open("/home/IRC/" + username + "/" + group_name2 + ".txt","a+").write(user + " to " + group_name2 + " -> "+message2 + "\n")
    def connectedToGroup(self, group_name,user_added,user_adding):
        for username in self.active_usernames:
            if username in self.groups[group_name]:
                self.connections[self.active_usernames.index(username)].send(bytes(" user "+bcolors.BOLD + user_adding + bcolors.ENDC +" added "+ bcolors.BOLD + bcolors.YELLOW  + user_added + bcolors.ENDC +" to group " + bcolors.BOLD +group_name + bcolors.ENDC + "\n", 'utf-8'))
                open(username + "_tmp.txt", "a").write("user "+bcolors.BOLD + user_adding + bcolors.ENDC +" added "+ bcolors.BOLD + bcolors.YELLOW  + user_added + bcolors.ENDC +" to group " + bcolors.BOLD +group_name + bcolors.ENDC)
    def removeFromGroup(self, group_name,user_added,user_adding):
        for username in self.active_usernames:
            if username in self.groups[group_name]:
                self.connections[self.active_usernames.index(username)].send(bytes(" user "+bcolors.BOLD + user_adding + bcolors.ENDC +" removed "+ bcolors.BOLD + bcolors.YELLOW  + user_added + bcolors.ENDC +" from group " + bcolors.BOLD +group_name + bcolors.ENDC, 'utf-8')) 
                open(username + "_tmp.txt", "a").write("user "+bcolors.BOLD + user_adding + bcolors.ENDC +" removed "+ bcolors.BOLD + bcolors.YELLOW  + user_added + bcolors.ENDC +" to group " + bcolors.BOLD +group_name + bcolors.ENDC + "\n")
    def dialogue(self, message2, after_dot):
        for user in self.all_usernames:
            if str(after_dot[1:after_dot.index(" ")]) == str(user):
                open("/home/IRC/"+user+"/@"+message2[1:message2.index(":")] + ".txt", "a+").write(message2[1:message2.index(":")+2]+ after_dot[after_dot.index(" "):]+"\n")
                open("/home/IRC/"+message2[1:message2.index(":")]+"/@"+ user + ".txt", "a+").write(after_dot[1+after_dot.index(" "):]+"\n")
                if(user in self.active_usernames):
                    self.connections[self.active_usernames.index(user)].send(bytes(" " +bcolors.BOLD + message2[1:message2.index(":")+2]+ bcolors.ENDC  + after_dot[after_dot.index(" ")+1:], 'utf-8'))
                    open(user+"_tmp.txt", "a+").write(bcolors.BOLD + message2[1:message2.index(":")+2]+ bcolors.ENDC  + after_dot[after_dot.index(" ")+1:] + "\n")
                break

    def waitToClean(self, time, users, current, msg):
        for user in users:
            if user in self.active_usernames and user is not current:
                self.connections[self.active_usernames.index(user)].send(bytes(msg, 'utf-8'))
        sleep(time)
        for user in users:
            if user in self.active_usernames:
                self.connections[self.active_usernames.index(user)].send(bytes("¹@£§½¬{[]}1q2w3e4r5t6y",'utf-8'))
        sleep(0.05)
        for user in users:
            f = open(user+"_tmp.txt","r").read()
            self.connections[self.active_usernames.index(user)].send(bytes(" " + str(f), 'utf-8'))

    def signal_handler(self, signal, frame):
        open("groups.txt", "w").write(str(self.groups))
        open("blocked.txt", "w").write(str(self.blocked_users))
        print('\nClosing server')
        #self.log_file.close()
        #file_pairs.close()
        sys.exit(0)
server = Server()
signal.signal(signal.SIGINT, server.signal_handler)
server.run()
