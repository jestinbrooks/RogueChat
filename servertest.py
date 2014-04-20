import socket
import select
import sys

# A script for testing server response to messages and commands from clients


def test(sock, test_message, name):
    if read(sock) == test_message:
        print "\033[32m Pass\033[0m : " + name
    else:
        print "\033[31m Fail\033[0m : " + name


def read(client_sock):
    """ Check for messages from the server sent to the socket client_sock """

    # Listen for input or a message and loop through all received messages
    read_sockets, write_sockets, error_sockets = select.select([client_sock], [], [])
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
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.settimeout(2)

    # Attempt to connect to server
    try:
        client_sock.connect((host, port))
    except socket.error:
        print 'Unable to connect'
        sys.exit()

    return client_sock

if len(sys.argv) > 1:
    host = sys.argv[1]
else:
    host = "localhost"

print "==== Tests for connecting to server ===="
# Test for correct server response to new connection
client_socket_one = connect(host)
test(client_socket_one, "\rWelcome to RogueChat: Please enter your name\n", "Connection-First client")

# Test for correct server response to entering a name
client_socket_one.send("name\n")
test(client_socket_one,
     "\rYou are in the Foyer. Enter #help for more information\n",
     "Enter Name-When connecting first client")

# Test for correct server response to entering an empty room
test(client_socket_one, "\rThe room is empty\n", "List occupants-Empty room")

# Test for correct server response to second new connection
client_socket_two = connect(host)
test(client_socket_two, "\rWelcome to RogueChat: Please enter your name\n", "Connection-Second client")

# Test for entering a name that is too long
client_socket_two.send("123456789012345678901234567890\n")
test(client_socket_two, "\rThat name is too long\n", "Enter name-Name over max length")

# Test for correct server response to entering a second name
client_socket_two.send("name2\n")
test(client_socket_two,
     "\rYou are in the Foyer. Enter #help for more information\n",
     "Enter name-When connecting second client")

# Test for correct server response to entering an occupied room
test(client_socket_two, "\rThe room contains: name\n", "List occupants-One occupant")

# Test for server notifying other occupants that client two has entered the room
test(client_socket_one, "\rname2 has entered the room\n", "Player enters room-Client one")

print "\n==== Tests for sending messages ===="
# Send a message from client one to client two
client_socket_one.send("hello\n")
test(client_socket_two, "\r<name> hello\n", "Send message-Client one to client two")

client_socket_two.send("hi\n")
test(client_socket_one, "\r<name2> hi\n", "Send message-Client two to client one")

print "\n==== Tests for changing room ===="
# Move client one to the Drawing Room
client_socket_one.send("#enter Drawing Room\n")
test(client_socket_one, "\rThe room is empty\n", "Enter command-Drawing room empty")
test(client_socket_two, "\rname has left the room\n", "Player leaves room-Client two")

# Try to move client one to room that doesn't exist
client_socket_one.send("#enter Bathroom\n")
test(client_socket_one, "\rThe door is locked\n", "Enter room-Invalid room name")

# Move client two to the drawing room
client_socket_two.send("#enter Drawing Room\n")
test(client_socket_two, "\rThe room contains: name\n", "Enter command-Drawing room one occupant")
test(client_socket_one, "\rname2 has entered the room\n", "Player enters room-Client one")

# Test for enter without a room name
client_socket_one.send("#enter\n")
test(client_socket_one, "\rYou must enter a room name\n", "Enter command-No param")

print "\n==== Tests for stabbing and creating new players ===="
# Test for stabbing another player
client_socket_two.send("#stab name\n")
test(client_socket_one, "\r<name2> Stabs you: Please enter a new name\n", "Stab-Client two to client one")

# Test entering new name after death
client_socket_one.send("name3\n")
test(client_socket_one,
     "\rYou are in the Foyer. Enter #help for more information\n",
     "Start over after death-Client one")
test(client_socket_one, "\rThe room is empty\n", "List occupants-After death empty room")

# Test notified of stabbing
test(client_socket_two, "\rname has been stabbed\n", "Notify of stabbing-Client two")

# Test stabbing player that isn't in the same room
client_socket_two.send("#stab name3\n")
test(client_socket_two, "\rThere is no name3 in this room\n", "Stab-Player not in room")

# Test client two stabbing itself
client_socket_two.send("#stab name2\n")
test(client_socket_two, "\r<name2> Stabs you: Please enter a new name\n", "Stab-Self client two")

# Test entering a name that is already in use
client_socket_two.send("name2\n")
test(client_socket_two, "\rThat name is either in use or dead\n", "Start over after death-Name that has been used")

# Test entering another name that is already in use
client_socket_two.send("Server\n")
test(client_socket_two,
     "\rThat name is either in use or dead\n",
     "Start over after death-Invalid name imitating the server")

# Test for entering new name after death with occupants in foyer
client_socket_two.send("name4\n")
test(client_socket_two,
     "\rYou are in the Foyer. Enter #help for more information\n",
     "Start over after death-Client two")
test(client_socket_two, "\rThe room contains: name3\n", "List occupants-After death client two")
test(client_socket_one, "\rname4 has entered the room\n", "Player enters room-After death client two")

# Test for stabbing an invalid name
client_socket_one.send("#stab invalid name\n")
test(client_socket_one, "\rThere is no invalid name in this room\n", "Stab-Invalid name")

# Test for stab with no name
client_socket_one.send("#stab\n")
test(client_socket_one, "\rYou must enter a name to stab\n", "Stab-No param")

print "\n==== Tests for other ===="
# Test entering an invalid command
client_socket_one.send("#run\n")
test(client_socket_one, "\rInvalid command\n", "Invalid command")

print "\n==== Tests the look command and room descriptions ===="
client_socket_two.send("#look\n")
test(client_socket_two,
     "\rYou are in the Foyer, It looks like a Foyer. \nThere are doors to the Dining Hall and Drawing Room\n"
     "The room contains: name3\n",
     "Look command-Clean in foyer with one occupant")

# Move to a room with contents without testing
client_socket_two.send("#enter Drawing Room\n")
read(client_socket_two)
read(client_socket_one)

client_socket_two.send("#look\n")
test(client_socket_two, "\rYou are in the Drawing Room, It looks like a Drawing Room. "
     "There are 2 bodies in a pool of blood on the floor. \n"
     "There are doors to the Foyer and Dining Hall\nThe room is empty\n",
     "Look command-Bodies and blood in empty drawing room")

client_socket_two.send("#clean\n")
client_socket_two.send("#look\n")
test(client_socket_two,
     "\rYou are in the Drawing Room, It looks like a Drawing Room. "
     "There are 2 bodies on the floor. \n"
     "There are doors to the Foyer and Dining Hall\nThe room is empty\n",
     "Look command-After cleaning but not hiding")

client_socket_two.send("#hide body\n")
client_socket_two.send("#look\n")
test(client_socket_two,
     "\rYou are in the Drawing Room, It looks like a Drawing Room. "
     "There is 1 body on the floor. \n"
     "There are doors to the Foyer and Dining Hall\nThe room is empty\n",
     "Look command-After hiding body")

client_socket_one.send("#hide item\n")
test(client_socket_one, "\rYou can't hide that\n", "Hide command-Invalid item")

# Move to a room with contents without testing
client_socket_two.send("#enter Foyer\n")
read(client_socket_two)
read(client_socket_one)

client_socket_two.send("#clean\n")
test(client_socket_one, "\r<name4> cleans up the blood\n", "Player is cleaning-Already clean room with one occupant")

client_socket_two.send("#hang a painting of mice\n")
test(client_socket_one, "\rname4 hangs something on the wall\n", "Player hangs art-Client one in Foyer")

client_socket_one.send("#look\n")
test(client_socket_one,
     "\rYou are in the Foyer, It looks like a Foyer. On the wall hangs a painting of mice. \n"
     "There are doors to the Dining Hall and Drawing Room\nThe room contains: name4\n",
     "Look command-With art")

client_socket_one.send("#steal art\n")
test(client_socket_two, "\rname3 takes something off the wall\n", "Player steals art-Client two in Foyer")

client_socket_one.send("#look\n")
test(client_socket_one,
     "\rYou are in the Foyer, It looks like a Foyer. \n"
     "There are doors to the Dining Hall and Drawing Room\nThe room contains: name4\n",
     "Look command-After stealing art")

# Test for adding and look at art with a description that is over the max length
client_socket_one.send("#hang 123456789012345678901234567890\n")
test(client_socket_two, "\rname3 hangs something on the wall\n", "Player hangs art-Client two in Foyer")
client_socket_one.send("#look\n")
test(client_socket_one,
     "\rYou are in the Foyer, It looks like a Foyer. On the wall hangs 12345678901234567890. \n"
     "There are doors to the Dining Hall and Drawing Room\nThe room contains: name4\n",
     "Look command-Art with description over max length")
client_socket_one.send("#steal art\n")
read(client_socket_two)

# Test for hanging art without a description
client_socket_one.send("#hang\n")
test(client_socket_one, "\rYou must enter a description of the art\n", "Hang command-No param")

print "\n==== Tests the look command and player descriptions ===="
client_socket_one.send("#look name3\n")
test(client_socket_one, "\rname3, They look nondescript\n", "Look at player-Self Default description")

client_socket_one.send("#describe has pretty tentacles")
client_socket_one.send("#look name3\n")
test(client_socket_one, "\rname3, has pretty tentacles\n", "Look at player-Self New description")

# Test for looking at another player with a default description
client_socket_one.send("#look name4\n")
test(client_socket_one, "\rname4, They look nondescript\n", "Look at player-Other default")

# Test for description over 20 chars
client_socket_one.send("#describe 123456789012345678901234567890\n")
client_socket_one.send("#look name3\n")
test(client_socket_one, "\rname3, 12345678901234567890\n", "Look at player-Description over max length")

client_socket_one.send("#look invalid\n")
test(client_socket_one, "\rThere is no invalid here", "Look at player-Invalid")

client_socket_one.send("#describe\n")
test(client_socket_one, "\rYou must enter a description of yourself\n", "describe command-No param")

print "\n==== Tests for quiting ===="
# Close connections
client_socket_one.send("#quit\n")
test(client_socket_one, "\nDisconnected from chat server", "Quit-Client one")
test(client_socket_two, "\rname3 disappears in a puff of smoke\n", "Player has quit message-Client two")

client_socket_two.send("#enter Dining Hall\n")
test(client_socket_two, "\rThe room is empty\n", "Room empty-Dining Hall")

client_socket_two.send("#enter Drawing Room\n")
test(client_socket_two, "\rThe room is empty\n", "Room empty-Drawing Room")

client_socket_two.send("#enter Foyer\n")
test(client_socket_two, "\rThe room is empty\n", "Room empty-Foyer")

del client_socket_two
client_socket_three = connect(host)

# Test for correct server response to new connection
test(client_socket_three, "\rWelcome to RogueChat: Please enter your name\n", "Connection-Third client")

# Test for correct server response to entering a name
client_socket_three.send("name5\n")


test(client_socket_three,
     "\rYou are in the Foyer. Enter #help for more information\n",
     "Enter Name-When connecting third client")
test(client_socket_three, "\rThe room contains: name4\n", "List occupants-One occupant disconnected incorrectly")

client_socket_three.send("Hello")
test(client_socket_three, "\rname4 disappears in a puff of smoke\n", "Player Disconnected-Exception in broadcast")
client_socket_three.send("#look")
test(client_socket_three,
     "\rYou are in the Foyer, It looks like a Foyer. \n"
     "There are doors to the Dining Hall and Drawing Room\nThe room is empty\n",
     "Look command-After improper disconnect and sending a message")

client_socket_three.send("#quit")
test(client_socket_three, "\nDisconnected from chat server", "Quit-Client three")
