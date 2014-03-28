import socket
import select
import sys

# A script for testing server response to messages and commands from clients


def test(sock, testmessage, name):
    if read(sock) == testmessage:
        print "\033[32m Pass\033[0m : " + name
    else:
        print "\033[31m Fail\033[0m : " + name

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

def connect():
    host = 'localhost'
    port = 5000

    # Create socket to connect to server
    clientsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsock.settimeout(2)

    # Attempt to connect to server
    try:
        clientsock.connect((host, port))
    except socket.error:
        print 'Unable to connect'
        sys.exit()

    return clientsock

clientsockone = connect()

# Test for correct server response to new connection
test(clientsockone, "\r<Server> Welcome to RogueChat: Please enter your name\n", "Connection")

# Test for correct server response to entering a name
clientsockone.send("name\n")
test(clientsockone, "\r<Server> You are in the Foyer\n", "Enter Name")

# Test for correct server response to entering an empty room
test(clientsockone, "\r<Server> The room is empty\n", "List occupants-Empty")

# Test for correct server response to new connection
clientsocktwo = connect()
test(clientsocktwo, "\r<Server> Welcome to RogueChat: Please enter your name\n", "Connection two")

# Test for correct server response to entering a name
clientsocktwo.send("name2\n")
test(clientsocktwo, "\r<Server> You are in the Foyer\n", "Enter name two")

# Test for correct server response to entering an occupied room
test(clientsocktwo, "\r<Server> The room contains: \nname\n", "List occupants")

# Test for server notifying other occupants that client two has entered the room
test(clientsockone, "\r<Server> name2 has entered the room\n", "Client two entered room")

# Send a message from client one to client two
clientsockone.send("hello\n")
test(clientsocktwo, "\r<name> hello\n", "Send message")

# Move client one to the Drawing Room
clientsockone.send("#enter Drawing Room\n")
test(clientsockone, "\r<Server> The room is empty\n", "Enter room-Empty")

test(clientsocktwo, "\r<Server> name has left the room\n", "Dead player left room")

# Try to move client one to room that doesn't exist
clientsockone.send("#enter Bathroom\n")
test(clientsockone, "\r<Server> not a room\n", "Enter room-Invalid")

# Test client two stab client one
clientsocktwo.send("#stab name\n")
test(clientsocktwo, "\r<Server> There is no name in this room\n", "Stab-Not in room")

clientsocktwo.send("#enter Drawing Room\n")
test(clientsocktwo, "\r<Server> The room contains: \nname\n", "Change room")

test(clientsockone, "\r<Server> name2 has entered the room\n", "Client two has entered room-Two")

clientsocktwo.send("#stab name\n")
test(clientsockone, "\r<name2> Stabs you: Please enter a new name\n", "Stab")

# Test entering new name after death
clientsockone.send("name3\n")
test(clientsockone, "\r<Server> You are in the Foyer\n", "New name")

test(clientsockone, "\r<Server> The room is empty\n", "List occupants-After death")

# Test notified of stabbing
test(clientsocktwo, "\r<Server> name has been stabbed", "Notify of stabbing")

# Test client two stabbing itself
clientsocktwo.send("#stab name2\n")
test(clientsocktwo, "\r<name2> Stabs you: Please enter a new name\n", "Stab self")

# Test entering a name that is already in use
clientsocktwo.send("name2\n")
test(clientsocktwo, "\r<Server> That name is either in use or dead\n", "New invalid name one")

# Test entering another name that is already in use
clientsocktwo.send("Server\n")
test(clientsocktwo, "\r<Server> That name is either in use or dead\n", "New invalid name two")

clientsocktwo.send("name4\n")
test(clientsocktwo, "\r<Server> You are in the Foyer\n", "New name two")

test(clientsocktwo, "\r<Server> The room contains: \nname3\n", "List occupants-After death two")

test(clientsockone, "\r<Server> name4 has entered the room\n", "Player enters room-After death two")

# Test entering an invalid command
clientsockone.send("#run\n")
test(clientsockone, "\r<Server> Invalid command\n", "Invalid command")

clientsockone.send("#stab invalid name\n")
test(clientsockone, "\r<Server> There is no invalid name in this room\n", "Stab invalid name")

clientsocktwo.send("#look\n")
test(clientsocktwo, "\r<Server> You are in the Foyer, It looks like a Foyer\n", "Look command part one")
test(clientsocktwo, "\r<Server> There are doors to the Dining Hall and Drawing Room\n\r<Server> The room contains: \nname3\n", "Look command part two")

# Close connections
clientsockone.send("#quit\n")
clientsocktwo.send("#quit\n")

read(clientsockone)
read(clientsocktwo)