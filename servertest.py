import socket
import select
import sys

# A script for testing server response to messages and commands from clients


def read(csock):
    """ Check for messages from the server sent to the socket csock """

    # Listen for input or a message and loop through all received messages
    read_sockets, write_sockets, error_sockets = select.select([csock], [], [])
    data = read_sockets[0].recv(4096)
    if not data:
        print '\nDisconnected from chat server'
        sys.exit()
    # Print messages from the server
    else:
        return data

host = 'localhost'
port = 5000

# Create socket to connect to server
clientsockone = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsockone.settimeout(2)

# Attempt to connect to server
try:
    clientsockone.connect((host, port))
except socket.error:
    print 'Unable to connect'
    sys.exit()

# Test for correct server response to new connection
if read(clientsockone) == "\r<Server> Welcome to RogueChat: Please enter your name\n":
    print "Connection: Pass"
else:
    print "Connection: Fail"

# Test for correct server response to entering a name
clientsockone.send("name\n")

if read(clientsockone) == "\r<Server> You are in the Foyer\n":
    print "Enter name: Pass"
else:
    print "Enter name: Fail"

# Test for correct server response to entering an empty room
if read(clientsockone) == "\r<Server> The room is empty\n":
    print "List occupants-Empty: Pass"
else:
    print "List occupants-Empty: Fail"


# Add second connection
clientsocktwo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocktwo.settimeout(2)

# Attempt to connect to server
try:
    clientsocktwo.connect((host, port))
except socket.error:
    print 'Unable to connect'
    sys.exit()

# Test for correct server response to new connection
if read(clientsocktwo) == "\r<Server> Welcome to RogueChat: Please enter your name\n":
    print "Connection two: Pass"
else:
    print "Connection two: Fail"

# Test for correct server response to entering a name
clientsocktwo.send("name2\n")

if read(clientsocktwo) == "\r<Server> You are in the Foyer\n":
    print "Enter name two: Pass"
else:
    print "Enter name two: Fail"

# Test for correct server response to entering an occupied room
if read(clientsocktwo) == "\r<Server> The room contains: \nname\n":
    print "List occupants: Pass"
else:
    print "List occupants: Fail"

# Test for server notifying other occupants that client two has entered the room
if read(clientsockone) == "\r<Server> name2 has entered the room\n":
    print "Client two has entered room: Pass"
else:
    print "Client two has entered room: Fail"

# Send a message from client one to client two
clientsockone.send("hello\n")

if read(clientsocktwo) == "\r<name> hello\n":
    print "Send message: Pass"
else:
    print "Send message: Fail"

# Move client one to the Drawing Room
clientsockone.send("#enter Drawing Room\n")

if read(clientsockone) == "\r<Server> The room is empty\n":
    print "Enter room-Empty: Pass"
else:
    print "Enter room-Empty: Fail"

# Try to move client one to room that doesn't exist
clientsockone.send("#enter Bathroom\n")

if read(clientsockone) == "\r<Server> not a room\n":
    print "Enter room-Invalid: Pass"
else:
    print "Enter room-Invalid: Fail"

# Test client two stab client one
clientsocktwo.send("#stab name\n")

if read(clientsocktwo) == "\r<Server> name has left the room\n":
    print "Dead player left room: Pass"
else:
    print "Dead player left room: Fail"

if read(clientsockone) == "\r<name2> Stabs you: Please enter a new name\n":
    print "Stab: Pass"
else:
    print "Stab: Fail"

# Test entering new name after death
clientsockone.send("name3\n")
if read(clientsockone) == "\r<Server> You are in the Foyer\n":
    print "New name: Pass"
else:
    print "New name: Fail"

if read(clientsockone) == "\r<Server> The room contains: \nname2\n":
    print "List occupants-After death: Pass"
else:
    print "List occupants-After death: Fail"

if read(clientsocktwo) == "\r<Server> name3 has entered the room\n":
    print "Player enters room-After death: Pass"
else:
    print "Player enters room-After death: Fail"

# Test client two stabbing itself
clientsocktwo.send("#stab name2\n")

if read(clientsocktwo) == "\r<name2> Stabs you: Please enter a new name\n":
    print "Stab self: Pass"
else:
    print "Stab self: Fail"

# Test entering a name that is already in use
clientsocktwo.send("name2\n")
if read(clientsocktwo) == "\r<Server> That name is either in use or dead\n":
    print "New invalid name one: Pass"
else:
    print "New invalid name one: Fail"


# Test entering another name that is already in use
clientsocktwo.send("Server\n")
if read(clientsocktwo) == "\r<Server> That name is either in use or dead\n":
    print "New invalid name two: Pass"
else:
    print "New invalid name two: Fail"

clientsocktwo.send("name4\n")
if read(clientsocktwo) == "\r<Server> You are in the Foyer\n":
    print "New name two: Pass"
else:
    print "New name two: Fail"

if read(clientsocktwo) == "\r<Server> The room contains: \nname3\n":
    print "List occupants-After death two: Pass"
else:
    print "List occupants-After death two: Fail"

if read(clientsockone) == "\r<Server> name4 has entered the room\n":
    print "Player enters room-After death two: Pass"
else:
    print "Player enters room-After death two: Fail"

# Close connections
clientsockone.send("#quit\n")
clientsocktwo.send("#quit\n")

read(clientsockone)
read(clientsocktwo)