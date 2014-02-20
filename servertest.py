import socket
import select
import sys

def read(csock):
    """ Check for messages from the server sent to the socket csock"""

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

# Close connections
clientsockone.send("#quit\n")
clientsocktwo.send("#quit\n")

read(clientsockone)
read(clientsocktwo)