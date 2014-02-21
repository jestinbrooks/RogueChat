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
    print "Enter Name: Pass"
else:
    print "Enter Name: Fail"

# Test for correct server response to entering an empty room
if read(clientsockone) == "\r<Server> The room is empty\n":
    print "List Occupants-Empty: Pass"
else:
    print "List Occupants-Empty: Fail"


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
    print "Connection Two: Pass"
else:
    print "Connection Two: Fail"

# Test for correct server response to entering a name
clientsocktwo.send("name2\n")

if read(clientsocktwo) == "\r<Server> You are in the Foyer\n":
    print "Enter Name Two: Pass"
else:
    print "Enter Name Two: Fail"

# Test for correct server response to entering an occupied room
if read(clientsocktwo) == "\r<Server> The room contains: \nname\n":
    print "List Occupants: Pass"
else:
    print "List Occupants: Fail"

# Test for server notifying other occupants that client two has entered the room
if read(clientsockone) == "\r<Server> name2 has entered the room\n":
    print "Client Two Has Entered Room: Pass"
else:
    print "Client Two Has Entered Room: Fail"

# Send a message from client one to client two
clientsockone.send("hello\n")

if read(clientsocktwo) == "\r<name> hello\n":
    print "Send Message: Pass"
else:
    print "send Message: Fail"

# Move client one to the Drawing Room
clientsockone.send("#enter Drawing Room\n")

if read(clientsockone) == "\r<Server> The room is empty\n":
    print "Enter Room-Empty: Pass"
else:
    print "Enter Room-Empty: Fail"

# Try to move client one to room that doesn't exist
clientsockone.send("#enter Bathroom\n")

if read(clientsockone) == "\r<Server> not a room\n":
    print "Enter Room-Invalid: Pass"
else:
    print "Enter Room-Invalid: Fail"

# Test client two stab client one
clientsocktwo.send("#stab name\n")

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
    print "List Occupants-after death: Pass"
else:
    print "List Occupants-after death: Fail"

# Close connections
clientsockone.send("#quit\n")
clientsocktwo.send("#quit\n")

read(clientsockone)
read(clientsocktwo)