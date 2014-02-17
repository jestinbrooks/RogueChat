import socket
import select
import sys

def read(socks):
    # Listen for input or a message and loop through all received messages
    read_sockets, write_sockets, error_sockets = select.select(socks, [], [])
    for sock in read_sockets:
        # If the message is from the server check if there is any data and then print
        if sock == clientsocket:
            data = sock.recv(4096)
            if not data:
                print '\nDisconnected from chat server'
                sys.exit()
            # Print messages from the server
            else:
                return data

host = 'localhost'
port = 5000

# Create socket to connect to server
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.settimeout(2)

# Attempt to connect to server
try:
    clientsocket.connect((host, port))
except socket.error:
    print 'Unable to connect'
    sys.exit()


sockets = [clientsocket]

if read(sockets) == "\r<Server> Welcome to RogueChat: Please enter your name\n":
    print "Connection: Pass"
else:
    print "Connection: Fail"

clientsocket.send("name")

if read(sockets) == "\r<Server> You are in the Foyer\n":
    print "Enter Name: Pass"
else:
    print "Enter Name: Fail"

if read(sockets) == "\r<Server> The room is empty\n":
    print "List Occupants: Pass"
else:
    print "List Occupants: Fail"

clientsocket.send("#quit")

print repr(read(sockets))