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
test(clientsockone, "\rWelcome to RogueChat: Please enter your name\n", "Connection-First client")

# Test for correct server response to entering a name
clientsockone.send("name\n")
test(clientsockone, "\rYou are in the Foyer. Enter #help for more information\n", "Enter Name-When connecting first client")

# Test for correct server response to entering an empty room
test(clientsockone, "\rThe room is empty\n", "List occupants-Empty room")

# Test for correct server response to second new connection
clientsocktwo = connect(host)
test(clientsocktwo, "\rWelcome to RogueChat: Please enter your name\n", "Connection-Second client")

# Test for entering a name that is too long
clientsocktwo.send("123456789012345678901234567890\n")
test(clientsocktwo, "\rThat name is too long\n", "Enter name-Name over max length")

# Test for correct server response to entering a second name
clientsocktwo.send("name2\n")
test(clientsocktwo, "\rYou are in the Foyer. Enter #help for more information\n", "Enter name-When connecting second client")

# Test for correct server response to entering an occupied room
test(clientsocktwo, "\rThe room contains: name\n", "List occupants-One occupant")

# Test for server notifying other occupants that client two has entered the room
test(clientsockone, "\rname2 has entered the room\n", "Player enters room-Client one")

print "\n==== Tests for sending messages ===="

# Send a message from client one to client two
clientsockone.send("hello\n")
test(clientsocktwo, "\r<name> hello\n", "Send message-Client one to client two")

clientsocktwo.send("hi\n")
test(clientsockone, "\r<name2> hi\n", "Send message-Client two to client one")

print "\n==== Tests for changing room ===="

# Move client one to the Drawing Room
clientsockone.send("#enter Drawing Room\n")
test(clientsockone, "\rThe room is empty\n", "Enter command-Drawing room empty")
test(clientsocktwo, "\rname has left the room\n", "Player leaves room-Client two")

# Try to move client one to room that doesn't exist
clientsockone.send("#enter Bathroom\n")
test(clientsockone, "\rThe door is locked\n", "Enter room-Invalid room name")

# Move client two to the drawing room
clientsocktwo.send("#enter Drawing Room\n")
test(clientsocktwo, "\rThe room contains: name\n", "Enter command-Drawing room one occupant")
test(clientsockone, "\rname2 has entered the room\n", "Player enters room-Client one")

# Test for enter without a room name
clientsockone.send("#enter\n")
test(clientsockone, "\rYou must enter a room name\n", "Enter command-No param")

print "\n==== Tests for stabbing and creating new players ===="

# Test for stabbing another player
clientsocktwo.send("#stab name\n")
test(clientsockone, "\r<name2> Stabs you: Please enter a new name\n", "Stab-Client two to client one")

# Test entering new name after death
clientsockone.send("name3\n")
test(clientsockone, "\rYou are in the Foyer. Enter #help for more information\n", "Start over after death-Client one")
test(clientsockone, "\rThe room is empty\n", "List occupants-After death empty room")

# Test notified of stabbing
test(clientsocktwo, "\rname has been stabbed\n", "Notify of stabbing-Client two")

# Test stabbing player that isn't in the same room
clientsocktwo.send("#stab name3\n")
test(clientsocktwo, "\rThere is no name3 in this room\n", "Stab-Player not in room")

# Test client two stabbing itself
clientsocktwo.send("#stab name2\n")
test(clientsocktwo, "\r<name2> Stabs you: Please enter a new name\n", "Stab-Self client two")

# Test entering a name that is already in use
clientsocktwo.send("name2\n")
test(clientsocktwo, "\rThat name is either in use or dead\n", "Start over after death-Name that has been used")

# Test entering another name that is already in use
clientsocktwo.send("Server\n")
test(clientsocktwo, "\rThat name is either in use or dead\n", "Start over after death-Invalid name imitating the server")

# Test for entering new name after death with occupants in foyer
clientsocktwo.send("name4\n")
test(clientsocktwo, "\rYou are in the Foyer. Enter #help for more information\n", "Start over after death-Client two")
test(clientsocktwo, "\rThe room contains: name3\n", "List occupants-After death client two")
test(clientsockone, "\rname4 has entered the room\n", "Player enters room-After death client two")

# Test for stabbing an invalid name
clientsockone.send("#stab invalid name\n")
test(clientsockone, "\rThere is no invalid name in this room\n", "Stab-Invalid name")

# Test for stab with no name
clientsockone.send("#stab\n")
test(clientsockone, "\rYou must enter a name to stab\n", "Stab-No param")

print "\n==== Tests for other ===="

# Test entering an invalid command
clientsockone.send("#run\n")
test(clientsockone, "\rInvalid command\n", "Invalid command")

print "\n==== Tests the look command and room descriptions ===="

clientsocktwo.send("#look\n")
test(clientsocktwo, "\rYou are in the Foyer, It looks like a Foyer. \n"
                    "There are doors to the Dining Hall and Drawing Room\n"
                    "The room contains: name3\n",
     "Look command-Clean in foyer with one occupant")

# Move to a room with contents without testing
clientsocktwo.send("#enter Drawing Room\n")
read(clientsocktwo)
read(clientsockone)

clientsocktwo.send("#look\n")
test(clientsocktwo, "\rYou are in the Drawing Room, It looks like a Drawing Room. "
     "There are 2 bodies in a pool of blood on the floor. \n"
     "There are doors to the Foyer and Dining Hall\nThe room is empty\n",
     "Look command-Bodies and blood in empty drawing room")

clientsocktwo.send("#clean\n")
clientsocktwo.send("#look\n")
test(clientsocktwo,
     "\rYou are in the Drawing Room, It looks like a Drawing Room. "
     "There are 2 bodies on the floor. \n"
     "There are doors to the Foyer and Dining Hall\nThe room is empty\n",
     "Look command-After cleaning but not hiding")

clientsocktwo.send("#hide body\n")
clientsocktwo.send("#look\n")
test(clientsocktwo,
     "\rYou are in the Drawing Room, It looks like a Drawing Room. "
     "There is 1 body on the floor. \n"
     "There are doors to the Foyer and Dining Hall\nThe room is empty\n",
     "Look command-After hiding body")

# Move to a room with contents without testing
clientsocktwo.send("#enter Foyer\n")
read(clientsocktwo)
read(clientsockone)

clientsocktwo.send("#clean\n")
test(clientsockone, "\r<name4> cleans up the blood\n", "Player is cleaning-Already clean room with one occupant")

clientsocktwo.send("#hang a painting of mice\n")
test(clientsockone, "\rname4 hangs something on the wall\n", "Player hangs art-Client one in Foyer")

clientsockone.send("#look\n")
test(clientsockone, "\rYou are in the Foyer, It looks like a Foyer. "
                    "On the wall hangs a painting of mice. \n"
                    "There are doors to the Dining Hall and Drawing Room\nThe room contains: name4\n",
     "Look command-With art")

clientsockone.send("#steal art\n")
test(clientsocktwo, "\rname3 takes something off the wall\n", "Player steals art-Client two in Foyer")

clientsockone.send("#look\n")
test(clientsockone,
     "\rYou are in the Foyer, It looks like a Foyer. \n"
     "There are doors to the Dining Hall and Drawing Room\nThe room contains: name4\n",
     "Look command-After stealing art")

# Test for adding and look at art with a description that is over the max length
clientsockone.send("#hang 123456789012345678901234567890\n")
test(clientsocktwo, "\rname3 hangs something on the wall\n", "Player hangs art-Client two in Foyer")
clientsockone.send("#look\n")
test(clientsockone,
     "\rYou are in the Foyer, It looks like a Foyer. On the wall hangs 12345678901234567890. \n"
     "There are doors to the Dining Hall and Drawing Room\nThe room contains: name4\n",
     "Look command-Art with description over max length")
clientsockone.send("#steal art\n")
read(clientsocktwo)

# Test for hanging art without a description
clientsockone.send("#hang\n")
test(clientsockone, "\rYou must enter a description of the art\n", "Hang command-No param")

print "\n==== Tests the look command and player descriptions ===="

clientsockone.send("#look name3\n")
test(clientsockone, "\rname3, They look nondescript\n", "Look at player-Self Default description")

clientsockone.send("#describe has pretty tentacles")
clientsockone.send("#look name3\n")
test(clientsockone, "\rname3, has pretty tentacles\n", "Look at player-Self New description")

# Test for looking at another player with a default description
clientsockone.send("#look name4\n")
test(clientsockone, "\rname4, They look nondescript\n", "Look at player-Other default")

# Test for description over 20 chars
clientsockone.send("#describe 123456789012345678901234567890\n")
clientsockone.send("#look name3\n")
test(clientsockone, "\rname3, 12345678901234567890\n", "Look at player-Description over max length")

clientsockone.send("#look invalid\n")
test(clientsockone, "\rThere is no invalid here", "Look at player-Invalid")

clientsockone.send("#describe\n")
test(clientsockone, "\rYou must enter a description of yourself\n", "describe command-No param")

print "\n==== Tests for quiting ===="

# Close connections
clientsockone.send("#quit\n")
test(clientsockone, "\nDisconnected from chat server", "Quit-Client one")
test(clientsocktwo, "\rname3 disappears in a puff of smoke\n", "Player has quit message-Client two")

clientsocktwo.send("#enter Dining Hall\n")
test(clientsocktwo, "\rThe room is empty\n", "Room empty-Dining Hall")

clientsocktwo.send("#enter Drawing Room\n")
test(clientsocktwo, "\rThe room is empty\n", "Room empty-Drawing Room")

clientsocktwo.send("#enter Foyer\n")
test(clientsocktwo, "\rThe room is empty\n", "Room empty-Foyer")

del clientsocktwo
clientsockthree = connect(host)

# Test for correct server response to new connection
test(clientsockthree, "\rWelcome to RogueChat: Please enter your name\n", "Connection-Third client")

# Test for correct server response to entering a name
clientsockthree.send("name5\n")


test(clientsockthree, "\rYou are in the Foyer. Enter #help for more information\n", "Enter Name-When connecting third client")
test(clientsockthree, "\rThe room contains: name4\n", "List occupants-One occupant disconnected incorrectly")

clientsockthree.send("Hello")
test(clientsockthree, "\rname4 disappears in a puff of smoke\n", "Player Disconnected-Exception in broadcast")
clientsockthree.send("#look")
test(clientsockthree,
     "\rYou are in the Foyer, It looks like a Foyer. \n"
     "There are doors to the Dining Hall and Drawing Room\nThe room is empty\n",
     "Look command-After improper disconnect and sending a message")

clientsockthree.send("#quit")
test(clientsockthree, "\nDisconnected from chat server", "Quit-Client three")
