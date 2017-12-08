import socket
import threading
import sys
import signal
import random
import os
import subprocess
import datetime
import glob

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
        self.all_usernames = open("users.txt", "r").read().split("\n")
        self.all_usernames.remove("")
        for i in self.all_usernames:
            self.blocked_users[i] = []
    def handler(self, c, a, user):
        while True:
            data = c.recv(1024)
            if data:
                data_str = str(data, 'utf-8')
                after_dot = data_str[data_str.index(":")+2:]
                open(user + "_tmp.txt", "a").write(after_dot + "\n")
                print(data_str)
                open("log_file.txt", "a").write(data_str + " at " +str(datetime.datetime.now()) +"\n")
                verify = data_str[0]
                verify_user = 0
                print("after dot:" + str(after_dot)+"ola")
                if (after_dot[0] == "*") and (len(after_dot) > 1) and (',' in after_dot) and after_dot.count("->") == 1 and len(after_dot[after_dot.index("->")+3:]) > 2:
                    group_name = after_dot[after_dot.index('->')+3:]
                    after_dot = after_dot[1:after_dot.index('->')-1].split(",")
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
                elif (after_dot[0] == "*") and (len(after_dot) > 1) and after_dot.count("->") == 0 and after_dot.count(" ") != 0 and after_dot.count(",") == 0:
                    group_name2 = after_dot[1:after_dot.index(" ")]
                    if(group_name2 in self.groups.keys()) and (user in self.groups[group_name2]):
                        message2 = after_dot[after_dot.index(" ")+1:]
                        cThread = threading.Thread(target=self.generatePrivateChat, args = (group_name2,message2, c, user))
                        cThread.daemon = True
                        cThread.start()
                    else:
                        c.send(bytes(" Group doesn't exist", "utf-8"))
                        open(user+"_tmp.txt", "a").write("Group doesn't exist")
                elif (after_dot[0] == "*") and (after_dot.count("->") != 1 or after_dot.count(" ") != 0):
                    c.send(bytes(" "+ bcolors.RED +"[hint] correct usage: *<user1>,<usern> -> <group_name> // *<group_name> message" + bcolors.ENDC, 'utf-8'))
                    open(user+"_tmp.txt", "a").write(bcolors.RED +"[hint] correct usage: *<user1>,<usern> -> <group_name> // *<group_name> message" + bcolors.ENDC+"\n")
                elif after_dot[0] is "@" and len(after_dot) == 1:
                    c.send(bytes(" " + str(self.active_usernames), 'utf-8'))
                    open(user+"_tmp.txt", "a").write(str(self.active_usernames) + "\n")
                elif after_dot[0] is "@" and len(after_dot) > 1 and (' ' in after_dot):
                    if(user not in self.blocked_users[after_dot[1:after_dot.index(" ")]] and after_dot[1:after_dot.index(" ")] not in self.blocked_users[user]):
                        cThread = threading.Thread(target=self.dialogue, args = (data_str,after_dot))
                        cThread.daemon = True
                        cThread.start()
                    else:
                        c.send(bytes(" blocked!", 'utf-8'))
                        open(user+"_tmp.txt", "a").write("blocked!\n")

                elif after_dot[0] is "@" and len(after_dot) > 1 and (' ' not in after_dot):
                    c.send(bytes(" "+bcolors.RED+"[hint] correct usage: @<user> <message> // @ to view users"+bcolors.ENDC+"\n", "utf-8"))
                    open(user+"_tmp.txt", "a").write(bcolors.RED+"[hint] correct usage: @<user> <message> // @ to view users"+bcolors.ENDC+"\n\n")

                elif after_dot[:5] == "!help":
                    c.send(bytes(" private chat: \n\t@<user> <message> // @ to see users\nprivate group: \n\tCREATE: *<user1>,<user2>,...<usern> -> <group_name> \n\tSEND MESSAGE: *<group_name> <message>\n\tADD USER: +<user> <group_name>\n\tREMOVE USER: -<user> <group_name>\nbanning users: ~<user_to_ban> to ban user and ~ again to unban\nlist chats: ls to list // ls <chat_name> to see specific chat\n ","utf-8"))
                    open(user+"_tmp.txt", "a").write("private chat: \n\t@<user> <message> // @ to see users\nprivate group: \n\tCREATE: *<user1>,<user2>,...<usern> -> <group_name> \n\tSEND MESSAGE: *<group_name> <message>\n\tADD USER: +<user> <group_name>\n\tREMOVE USER: -<user> <group_name>\nbanning users: ~<user_to_ban> to ban user and ~ again to unban\nlist chats: ls to list // ls <chat_name> to see specific chat\n \n")
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
                                open(user + "_tmp.txt", "a").write("group doesn't exist\n")

                        else:
                            c.send(bytes(" user already in group", 'utf-8'))
                            open(user+"_tmp.txt", "a").write("user already in group\n")
                    elif (after_dot.count(" ") == 0) and after_dot[1:] in self.groups.keys():
                        c.send(bytes(" " + str(self.groups[after_dot[1:]]), 'utf-8'))
                        open(user+"_tmp.txt", "a").write(str(self.groups[after_dot[1:]])+"\n")
                    else:
                        c.send(bytes(" group doesn't exist","utf-8"))
                        open(user + "_tmp.txt", "a").write("group doesn't exist\n")
                elif after_dot[0] is "-":
                    if (after_dot.count(" ") == 1) and (after_dot[1:after_dot.index(" ")] in self.all_usernames) and (after_dot[after_dot.index(" ")+1:] in self.groups.keys()):
                        if after_dot[1:after_dot.index(" ")] in self.groups[after_dot[after_dot.index(" ")+1:]] and after_dot[1:after_dot.index(" ")] in self.all_usernames:
                            if user in self.groups[after_dot[after_dot.index(" ")+1:]]:
                                self.groups[after_dot[after_dot.index(" ")+1:]].remove(after_dot[1:after_dot.index(" ")])
                            else:
                                c.send(bytes(" group doesn't exist","utf-8"))
                                open(user+"_tmp.txt", "a").write("group doesn't exist\n")
                        else:
                            c.send(bytes(" group doesn't exist", 'utf-8'))
                            open(user+"_tmp.txt", "a").write("group doesn't exist\n")

                    elif (after_dot.count(" ") == 0) and after_dot[1:] in self.groups.keys():
                        c.send(bytes(" " + str(self.groups[after_dot[1:]]), 'utf-8'))
                        open(user + "_tmp.txt", "a").write(str(self.groups[after_dot[1:]])+"\n")
                    else:
                        c.send(bytes(" group doesn't exist","utf-8"))
                        open(user+"_tmp.txt", "a").write("group doesn't exist\n")


                elif after_dot[0] is "~":
                    if len(after_dot) > 1 and after_dot[1:] in self.all_usernames:
                        if after_dot[1:] not in self.blocked_users[user]:
                            self.blocked_users[user].append(after_dot[1:])
                        elif len(after_dot) == 1:
                            self.blocked_users[user].remove(after_dot[1:])
                        else:
                            c.send(bytes(" "+bcolors.RED+"[hint] correct usage: ~<user>\n"+bcolors.ENDC, "utf-8"))
                            open(user+"_tmp.txt" + "a").write(bcolors.RED+"[hint] correct usage: ~<user>\n"+bcolors.ENDC+"\n")

                    else:
                        c.send(bytes(" "+str(self.blocked_users[user]), "utf-8"))
                        open(user + "_tmp.txt").write(str(self.blocked_users[user]) + "\n")
                elif after_dot == "ls":
                    filenames = glob.glob("/home/IRC/"+user+"/*.txt")
                    names = []
                    for f in filenames:
                        names.append(f[f.index("IRC/")+8:f.index(".txt")])
                    c.send(bytes(" "+str(names), 'utf-8'))
                    open(user + "_tmp.txt", "a").write(str(names)+"\n")
                elif after_dot[:2] == "ls" and after_dot.count(" ") == 1 and len(after_dot[3:]) > 0:
                    filenames = glob.glob("/home/IRC/"+user+"/*.txt")
                    names = []
                    for f in filenames:
                        names.append(f[f.index("IRC/")+8:f.index(".txt")])
                    for n in names:
                        if n == after_dot[3:]:
                            t = open("/home/IRC/"+user+"/"+n+".txt","r").readlines()
                            for line in t:
                                if line != "////@£§£½§¬½{[{[.read until here.\n":
                                    c.send(bytes(" "+str(line), 'utf-8'))
                                    open(user+"_tmp.txt", "a").write(str(t) + "\n")
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
                                    open(user + "_tmp.txt" + "a").write(str(i)+"\n")
                    f = open("/home/IRC/"+user+"/"+n+".txt","r")
                    lines = f.readlines()
                    f.close()
                    f = open("/home/IRC/"+user+"/"+n+".txt", "w")
                    for line in lines:
                        if line!="////@£§£½§¬½{[{[.read until here.\n":
                            f.write(line)
                    f.close()
                else:
                    for connection in self.connections:
                        #change to inactive too && see if user that sends is blocked in other users
                        if(connection is not c and self.active_usernames[self.connections.index(connection)] not in self.blocked_users[user]) and user not in self.blocked_users[self.active_usernames[self.connections.index(connection)]]:
                            connection.send(bytes(" [GLOBAL] " + data_str[1:], "utf-8"))
                            open(self.active_usernames[self.connections.index(connection)], "a").write("[GLOBAL] " + data_str[1:] + "\n")
            else:
                filenames = glob.glob("/home/IRC/"+ user +"/*.txt")
                for f in filenames:
                    open(f,"a").write("////@£§£½§¬½{[{[.read until here.\n")
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
                        open(user + "_tmp.txt", "a").write("welcome back, "+ user +"!!\n\n")
                        print(user + " connected")
                        filenames = glob.glob("/home/IRC/" + user + "/*.txt")
                        for f in filenames:
                            lines = open(f, "r").readlines()
                            if len(lines) > 0:
                                if lines[len(lines)-1] != "////@£§£½§¬½{[{[.read until here.\n":
                                    c.send(bytes("\n"+bcolors.RED + "you've got new messages in " + bcolors.BOLD +f[f.index(user)+len(user)+1:len(f)-4]+ bcolors.ENDC + bcolors.RED +" [type ls " + f[f.index(user)+len(user)+1:len(f)-4]+" to see]"+bcolors.ENDC+"\n",'utf-8'))
                                    open(user + "_tmp.txt", "a").write(bcolors.RED + "you've got new messages in " + bcolors.BOLD +f[f.index(user)+len(user)+1:len(f)-4]+ bcolors.ENDC + bcolors.RED +" [type ls " + f[f.index(user)+len(user)+1:len(f)-4]+" to see]"+bcolors.ENDC+"\n\n")
                                    
                    else:
                        c.send(bytes(" welcome to IRCHAT, "+ user +"!!\n",'utf-8'))
                        open(user + "_tmp.txt", "a").write("welcome to IRCHAT, "+ user +"!!\n\n")
                        open("users.txt","a").write(user+"\n")
                        print(user + " connected and added to database")
                        path = "/home/IRC/"+user+"/"
                        os.makedirs(path)
                        open(path+user+"_GLOBAL.txt","w+")

                    c.send(bytes("\npress !help to see the chat's manual\n\n",'utf-8'))
                    open(user+"_tmp.txt", "a").write("press !help to see the chat's manual\n\n\n")
                    self.connections.append(c)
                    c.send(bytes(" "+ str(len(self.active_usernames)) + ' connected clients: ' + ', '.join(self.active_usernames) +'\n', 'utf-8'))
                    open(user+"_tmp.txt", "a").write(str(len(self.active_usernames)) + ' connected clients: ' + ', '.join(self.active_usernames) +'\n\n')
                    for connection in self.connections:
                        if connection is not c:
                            connection.send(bytes(" "+ user +" connected\n", 'utf-8'))
                            open(self.active_usernames[self.connections.index(connection)]+"_tmp.txt", "a").write(" "+ user +" connected\n\n")
                    cThread = threading.Thread(target=self.handler, args=(c, a, user))
                    cThread.daemon = True
                    cThread.start()
                    self.active_usernames.append(user)
                    self.all_usernames.append(user)
                    self.blocked_users[user] = []
                else:
                    c.send(bytes(" user already connected", 'utf-8'))
                    open(user+"_tmp.txt", "a").write("user already connected\n")
                    c.close()
            else:
                c.send(bytes(" username cannot contain special characters such as ' *@+-~:lsexit'", 'utf-8'))
                open(user+"_tmp.txt", "a").write("username cannot contain special characters such as ' *@+-~:lsexit'\n")
                c.close()
    def generatePrivateChat(self, group_name2, message2, c, user):
        for connection in self.connections:
            if self.active_usernames[self.connections.index(connection)] in self.groups[group_name2]:
                if connection is not c:
                    connection.send(bytes(" "+ user + " to " + str(group_name2) +" -> " + message2,"utf-8"))
                    open(self.active_usernames[self.connections.index(connection)]+"_tmp.txt", "a").write(user + " to " + str(group_name2) +" -> " + message2)
        for username in self.all_usernames:
            if username in self.groups[group_name2]:
                if username == user:
                    open("/home/IRC/" + username + "/" + group_name2 + ".txt","a").write(message2 + "\n")
                else:
                    open("/home/IRC/" + username + "/" + group_name2 + ".txt","a").write(user + " to " + group_name2 + " -> "+message2 + "\n")
    def connectedToGroup(self, group_name,user_added,user_adding):
        for username in self.active_usernames:
            if username in self.groups[group_name]:
                self.connections[self.active_usernames.index(username)].send(bytes(" user "+bcolors.BOLD + user_adding + bcolors.ENDC +" added "+ bcolors.BOLD + bcolors.YELLOW  + user_added + bcolors.ENDC +" to group " + bcolors.BOLD +group_name + bcolors.ENDC, 'utf-8'))

    def dialogue(self, message2, after_dot):
            for user in self.all_usernames:
                if str(after_dot[1:after_dot.index(" ")]) == str(user):
                    open("/home/IRC/"+user+"/@"+message2[1:message2.index(":")] + ".txt", "a").write(message2[1:message2.index(":")+2]+ after_dot[after_dot.index(" "):]+"\n")
                    open("/home/IRC/"+message2[1:message2.index(":")]+"/@"+ user + ".txt", "a").write(after_dot[1+after_dot.index(" "):]+"\n")
                    if(user in self.active_usernames):
                        self.connections[self.active_usernames.index(user)].send(bytes(message2[:message2.index(":")+2]+ after_dot[after_dot.index(" "):], 'utf-8'))
                        open(user+"_tmp.txt", "a").write(message2[1:message2.index(":")+2]+ after_dot[after_dot.index(" "):] + "\n")
                    break

def signal_handler(signal, frame):
        print('Good bye!')
        #self.log_file.close()
        #file_pairs.close()
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
server = Server()
server.run()
