# IRChat
Simple chat in python. It is possible to send a global message to every connected client, a private message to a particular client or even create chat groups.
##How to run
In the server machine:
```
python3.6 server.py
```
In each client machine:
```
python3.6 client.py <server_IP_address>
```
##How to use
A brief description of how to use this chat
### Global messages
Global messages are sent to everyone that is connected. In order to do that, just type your message:
```
Hello World!
```
###Private chat
This will send a message to a particular person which username is writen after the @:
```
@ <user> <message> // @ to see users
```
###Chat group
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

###Blocking a user
It is even possible to block/unblock a certain user by writing its username after ~ like this:
```
~<user_to_block/unblock>
```
