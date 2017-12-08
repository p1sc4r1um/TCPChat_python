# IRChat
TCP chat in python that runs with sockets and threads. It is possible to send a global message to every connected client (or disconnected that can read that message later), a private message to a particular client, create chat groups and block users if needed. Every message can be normal or timed (after x seconds is erased and no records of that is kept).

## How it works
There's a server machine that manages multiple clients. The server stats and searchs in database for previous conversations, groups or functionalities needed. Server is always listening for new connections and when it receives one connection, one thread (handler) is assigned to that connection and manages it. To simplify the program's testing, the server binds in random TCP port and when one client is ran in the same machine it  searchs for open TCP ports with command *"str(subprocess.getoutput("lsof -Pn -i4 | grep TCP"))"* and connects to the server's TCP port. 
After, the username is asked. If that user have never logged to the chat a welcome message is shown and the needed files are created. Otherwise, the list of chats with unread messages is shown to the client and a welcome back message is sent.
The handler job is to check if the message sent by the client is a command or a simple global message and send it to the correct destination users, with help of their functions.
Every client will have its folder created *(/home/IRC/\<user\>)* in the server machine, which will have the contents of every chat group and dialogue conversation he is in, so that when he lists the conversation it is shown in the client's terminal. Also, a temporary file exists *(/\<user\>_tmp.txt)* while each client is connected, which will have the recording of every message and command sent and received by that client. That way, hen he receives a temporary message, the terminal can be cleaned up and the history printed again.
When the client exits the program, the temporary file is eliminated, his information is saved in server files and the information of the messages read by that user are saved in each conversation file so that when that user reconnects, a message with conversations with unread messages is shown.

## How to run
In the server machine:
```
sudo python3 server.py 
```
###### (sudo may be needed because program needs permissions to create and remove folders on server machine)

In each client machine:
```
python3 client.py <server_IP_address>
```
## How to use
A brief description of how to use this chat

### Global messages
Global messages are sent to everyone connected. In order to do that, just type your message:
```
Hello World!
```
### Private chat
This will send a message to a particular person which username is writen after the @:
```
@ <user> <message> // @ to see users
```
### Chat group
it is possible to create a group by specifying which users to include in the group besides yourself. Users are written after the * and sparated by commas(,):
```
*<user1>,<user2>,...<usern> -> <group_name>
```
To send a message to a certain group you write the group name after the * and then the message:
```
 *<group_name> <message>
```
To add a user to the group do the following:
```
 +<user> <group_name>
```
And to remove:
```
-<user> <group_name>
```

### List chats
When you want to see some chat history there are two options:
1. Search the chat and next list it
```
ls to see the user's chats // ls <chat_name> to list it
```
2. List 
```
ls <chat_name> to list chat_name
```

### Blocking a user
It is even possible to block/unblock a certain user by writing its username after ~ like this:
```
~<user_to_block/unblock>
```

### Timed messages
temporary messages (messages with associated expiration time in seconds) can be send in: 
1. Groups
```
*<time>*<group_name> <message>
```
2. Private
```
*<time>@<username> <message>
```

### Exit the program
To exit the program you can press control C or just type exit
```
exit
```
