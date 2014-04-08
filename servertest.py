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
        return '\nDisconnected from chat server'
        #sys.exit()
    # Print messages from the server
    else:
        return data


def connect(host):
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

if len(sys.argv) > 1:
    host = sys.argv[1]
else:
    host = "localhost"

clientsockone = connect(host)

print "==== Tests for connecting to server ===="

# Test for correct server response to new connection
test(clientsockone, "\r<Server> Welcome to RogueChat: Please enter your name\n", "Connection-First client")

# Test for correct server response to entering a name
clientsockone.send("name\n")
test(clientsockone, "\r<Server> You are in the Foyer. Enter #help for more information\n", "Enter Name-When connecting first client")

# Test for correct server response to entering an empty room
test(clientsockone, "\r<Server> The room is empty\n", "List occupants-Empty room")

# Test for correct server response to new connection
clientsocktwo = connect(host)
test(clientsocktwo, "\r<Server> Welcome to RogueChat: Please enter your name\n", "Connection-Second client")

# Test for correct server response to entering a name
clientsocktwo.send("name2\n")
test(clientsocktwo, "\r<Server> You are in the Foyer. Enter #help for more information\n", "Enter name-When connecting second client")

# Test for correct server response to entering an occupied room
test(clientsocktwo, "\r<Server> The room contains: \nname\n", "List occupants-One occupant")

# Test for server notifying other occupants that client two has entered the room
test(clientsockone, "\r<Server> name2 has entered the room\n", "Player enters room-Client one")

# Send a message from client one to client two
clientsockone.send("hello\n")
test(clientsocktwo, "\r<name> hello\n", "Send message-Client one to client two")

print "\n==== Tests for changing room ===="

# Move client one to the Drawing Room
clientsockone.send("#enter Drawing Room\n")
test(clientsockone, "\r<Server> The room is empty\n", "Enter command-Drawing room empty")

test(clientsocktwo, "\r<Server> name has left the room\n", "Player leaves room-Client two")

# Try to move client one to room that doesn't exist
clientsockone.send("#enter Bathroom\n")
test(clientsockone, "\r<Server> not a room\n", "Enter room-Invalid room name")

print "\n==== Tests for stabbing and creating new players ===="

# Test client two stab client one
clientsocktwo.send("#stab name\n")
test(clientsocktwo, "\r<Server> There is no name in this room\n", "Stab-Invalid name")

clientsocktwo.send("#enter Drawing Room\n")
test(clientsocktwo, "\r<Server> The room contains: \nname\n", "Enter command-Drawing room one occupant")

test(clientsockone, "\r<Server> name2 has entered the room\n", "Player enters room-Client one")

clientsocktwo.send("#stab name\n")
test(clientsockone, "\r<name2> Stabs you: Please enter a new name\n", "Stab-Client two to client one")

# Test entering new name after death
clientsockone.send("name3\n")
test(clientsockone, "\r<Server> You are in the Foyer. Enter #help for more information\n", "Start over after death-Client one")

test(clientsockone, "\r<Server> The room is empty\n", "List occupants-After death empty room")

# Test notified of stabbing
test(clientsocktwo, "\r<Server> name has been stabbed\n", "Notify of stabbing-Client two")

# Test client two stabbing itself
clientsocktwo.send("#stab name2\n")
test(clientsocktwo, "\r<name2> Stabs you: Please enter a new name\n", "Stab-Self client two")

# Test entering a name that is already in use
clientsocktwo.send("name2\n")
test(clientsocktwo, "\r<Server> That name is either in use or dead\n", "Start over after death-Name that has been used")

# Test entering another name that is already in use
clientsocktwo.send("Server\n")
test(clientsocktwo, "\r<Server> That name is either in use or dead\n", "Start over after death-Imitating the server")

clientsocktwo.send("name4\n")
test(clientsocktwo, "\r<Server> You are in the Foyer. Enter #help for more information\n", "Start over after death-Client two")

test(clientsocktwo, "\r<Server> The room contains: \nname3\n", "List occupants-After death client two")

test(clientsockone, "\r<Server> name4 has entered the room\n", "Player enters room-After death client two")

print "\n==== Tests for invalid commands ===="

# Test entering an invalid command
clientsockone.send("#run\n")
test(clientsockone, "\r<Server> Invalid command\n", "Invalid command")

clientsockone.send("#stab invalid name\n")
test(clientsockone, "\r<Server> There is no invalid name in this room\n", "Stab-Invalid name")

print "\n==== Tests the look command and room descriptions ===="

clientsocktwo.send("#look\n")
test(clientsocktwo, "\r<Server> You are in the Foyer, It looks like a Foyer. \n"
                    "There are doors to the Dining Hall and Drawing Room\n"
                    "The room contains: \nname3\n",
     "Look command-Clean in foyer with one occupant")

# Move to a room with contents without testing
clientsocktwo.send("#enter Drawing Room\n")
read(clientsocktwo)
read(clientsockone)

clientsocktwo.send("#look\n")
test(clientsocktwo, "\r<Server> You are in the Drawing Room, It looks like a Drawing Room. "
     "There are 2 bodies in a pool of blood on the floor. \n"
     "There are doors to the Foyer and Dining Hall\nThe room is empty\n",
     "Look command-Bodies and blood in empty drawing room")

clientsocktwo.send("#clean\n")
clientsocktwo.send("#look\n")
test(clientsocktwo,
     "\r<Server> You are in the Drawing Room, It looks like a Drawing Room. "
     "There are 2 bodies on the floor. \n"
     "There are doors to the Foyer and Dining Hall\nThe room is empty\n",
     "Look command-After cleaning but not hiding")

clientsocktwo.send("#hide body\n")
clientsocktwo.send("#look\n")
test(clientsocktwo,
     "\r<Server> You are in the Drawing Room, It looks like a Drawing Room. "
     "There is 1 body on the floor. \n"
     "There are doors to the Foyer and Dining Hall\nThe room is empty\n",
     "Look command-After hiding body")

# Move to a room with contents without testing
clientsocktwo.send("#enter Foyer\n")
read(clientsocktwo)
read(clientsockone)

clientsocktwo.send("#clean\n")
test(clientsockone, "\r<name4> cleans up the blood\n", "Player is cleaning-Already clean room with one occupant")

clientsocktwo.send("#hang painting of mice\n")
test(clientsockone, "\r<Server> name4 hangs something on the wall\n", "Player hangs art-Client one in Foyer")

clientsockone.send("#look\n")
test(clientsockone, "\r<Server> You are in the Foyer, It looks like a Foyer. "
                    "On the wall hangs a painting of mice. \n"
                    "There are doors to the Dining Hall and Drawing Room\nThe room contains: \nname4\n",
     "Look command-With art")

clientsockone.send("#steal art\n")
test(clientsocktwo, "\r<Server> name3 takes something off the wall\n", "Player steals art-Client two in Foyer")

clientsockone.send("#look\n")
test(clientsockone,
     "\r<Server> You are in the Foyer, It looks like a Foyer. \n"
     "There are doors to the Dining Hall and Drawing Room\nThe room contains: \nname4\n",
     "Look command-After stealing art")

print "\n==== Tests the look command and player descriptions ===="

clientsockone.send("#look name3\n")
test(clientsockone, "\r<Server> name3, They look nondescript\n", "Look at player-Self Default description")

clientsockone.send("#describe has pretty tentacles")
clientsockone.send("#look name3\n")
test(clientsockone, "\r<Server> name3, has pretty tentacles\n", "Look at player-Self New description")

clientsockone.send("#look name4\n")
test(clientsockone, "\r<Server> name4, They look nondescript\n", "Look at player-Other default")

clientsockone.send("#look invalid\n")
test(clientsockone, "\r<Server> There is no invalid here", "Look at player-invalid")

print "\n==== Tests for quiting ===="

# Close connections
clientsockone.send("#quit\n")
test(clientsockone, "\nDisconnected from chat server", "Quit-Client one")
test(clientsocktwo, "\r<Server> name3 disappears in a puff of smoke\n", "Player has quit message-Client two")

clientsocktwo.send("#enter Dining Hall\n")
test(clientsocktwo, "\r<Server> The room is empty\n", "Room empty-Dining Hall")

clientsocktwo.send("#enter Drawing Room\n")
test(clientsocktwo, "\r<Server> The room is empty\n", "Room empty-Drawing Room")

clientsocktwo.send("#enter Foyer\n")
test(clientsocktwo, "\r<Server> The room is empty\n", "Room empty-Foyer")

del clientsocktwo
clientsockthree = connect(host)

# Test for correct server response to new connection
test(clientsockthree, "\r<Server> Welcome to RogueChat: Please enter your name\n", "Connection-Third client")

# Test for correct server response to entering a name
clientsockthree.send("name5\n")


test(clientsockthree, "\r<Server> You are in the Foyer. Enter #help for more information\n", "Enter Name-When connecting third client")
test(clientsockthree, "\r<Server> The room contains: \nname4\n", "List occupants-One occupant disconnected incorrectly")

clientsockthree.send("Hello")
clientsockthree.send("#look")
test(clientsockthree,
     "\r<Server> You are in the Foyer, It looks like a Foyer. \n"
     "There are doors to the Dining Hall and Drawing Room\nThe room is empty\n",
     "Look command-After improper disconnect and sending a message")

clientsockthree.send("#quit")
test(clientsockthree, "\nDisconnected from chat server", "Quit-Client three")
