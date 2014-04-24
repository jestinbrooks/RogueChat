
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

# setup connections without quiting
client_socket_one = connect(host)
read(client_socket_one)
client_socket_one.send("name\n")
read(client_socket_one)
read(client_socket_one)
client_socket_two = connect(host)
read(client_socket_two)
client_socket_two.send("name2\n")
read(client_socket_two)
read(client_socket_two)
read(client_socket_one)

print "==== Tests for 3 clients ===="

# Test for correct server response to new connection
client_socket_three = connect(host)
test(client_socket_three, "\rWelcome to RogueChat: Please enter your name\n", "Connection-Third client")

# Test for correct server response to entering a name
client_socket_three.send("name3\n")
test(client_socket_three,
     "\rYou are in the Foyer. Enter #help for more information\n",
     "Enter Name-When connecting third client")
test(client_socket_three, "\rThe room contains: name, name2\n", "List occupants-3rd client")

# Test for third client entering room
test(client_socket_one, "\rname3 has entered the room\n", "Enter room-3rd client part one")
test(client_socket_two, "\rname3 has entered the room\n", "Enter room-3rd client part two")

client_socket_three.send("hi\n")
test(client_socket_one, "\r<name3> hi\n", "Message-3 clients part one")
test(client_socket_two, "\r<name3> hi\n", "Message-3 clients part two")

print "\n==== Tests the look command and player descriptions ===="

client_socket_one.send("#look name\n")
test(client_socket_one, "\rname, They look nondescript\n", "Look at player-Self Default description")

client_socket_one.send("#describe has pretty tentacles")
client_socket_one.send("#look name\n")
test(client_socket_one, "\rname, has pretty tentacles\n", "Look at player-Self New description")

# Test for looking at another player with a default description
client_socket_one.send("#look name2\n")
test(client_socket_one, "\rname2, They look nondescript\n", "Look at player-Other default")

# Test for description over 20 chars
client_socket_one.send("#describe 123456789012345678901234567890\n")
client_socket_one.send("#look name\n")
test(client_socket_one, "\rname, 12345678901234567890\n", "Look at player-Description over max length")

client_socket_one.send("#look invalid\n")
test(client_socket_one, "\rThere is no invalid here", "Look at player-Invalid")

client_socket_one.send("#describe\n")
test(client_socket_one, "\rYou must enter a description of yourself\n", "describe command-No param")

print "\n==== Tests for quit and disconnecting ===="

del client_socket_two

client_socket_one.send("#look\n")
test(client_socket_one,
     "\rYou are in the Foyer, It looks like a Foyer. \n"
     "There are doors to the Dining Hall and Drawing Room\n"
     "The room contains: name2, name3\n",
     "Look-Bad disconnect before message sent")

# Test for sending a message when a play has disconnected improperly
client_socket_three.send("Hello")
read(client_socket_one)
client_socket_one.send("test")
test(client_socket_one, "\rname2 disappears in a puff of smoke\n", "Player Disconnected-Exception in broadcast part 1")
test(client_socket_three, "\rname2 disappears in a puff of smoke\n", "Player Disconnected-Exception in broadcast part 2")

# Test for making sure a improperly disconnected player is removed from the room
client_socket_three.send("#look")
test(client_socket_three,
     "\rYou are in the Foyer, It looks like a Foyer. \n"
     "There are doors to the Dining Hall and Drawing Room\nThe room contains: name\n",
     "Look command-After improper disconnect and sending a message")

# Test with a proper disconnection
client_socket_one.send("#quit")
test(client_socket_one, "\nDisconnected from chat server", "Quit-Client one")
test(client_socket_three, "\rname disappears in a puff of smoke\n", "Player Disconnected-Quit command")

# Test that all rooms are empty
client_socket_three.send("#enter Dining Hall\n")
test(client_socket_three, "\rThe room is empty\n", "Room empty-Dining Hall")
client_socket_three.send("#enter Drawing Room\n")
test(client_socket_three, "\rThe room is empty\n", "Room empty-Drawing Room")
client_socket_three.send("#enter Foyer\n")
test(client_socket_three, "\rThe room is empty\n", "Room empty-Foyer")

client_socket_three.send("#quit")
test(client_socket_three, "\nDisconnected from chat server", "Quit-Client three")