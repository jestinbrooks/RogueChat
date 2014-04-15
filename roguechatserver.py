import socket
import select

import config
from objects import Room, Client


#######################################
# Functions for sending messages
#######################################
def broadcast(originclient, oname, message):
    """ Send a message to all occupants of a room """
    for client in originclient.room.occupantslist:
        if client.clientsock != originclient.clientsock:
            try:
                output = "\r<%s> %s" % (oname, message)
                client.clientsock.getpeername()
                client.clientsock.send(output)
            except socket.error:
                print "Client %s is offline\n" % client.clientsock
                client.clientsock.close()
                originclient.room.removeoccupant(client)
                socket_list.remove(client.clientsock)
                del clients[client.clientsock]


def send(originname, destclient, message):
    """ Send a message to one user """
    try:
        output = "\r<%s> %s" % (originname, message)
        destclient.clientsock.getpeername()
        destclient.clientsock.send(output)
    except socket.error:
        print "Client %s is offline\n" % destclient.name
        destclient.clientsock.close()
        destclient.room.removeoccupant(destclient)
        socket_list.remove(destclient.clientsock)
        del clients[destclient.clientsock]


def server_message(client_list, message):
    """ Send a message from the server to a list of clients """
    message = "\r%s" % message
    for client in client_list:
        client.clientsock.send(message)


############################
# Command functions
############################
def rc_help(client, data):
    """ Function for executing the help command. Which gives a list of commands. """
    server_message([client], config.helptext)


def enter(client, data):
    """ Function for executing the enter command. Which moves the player to a new room. """
    # if valid room is entered, enter room and list occupants
    if data[7:-1]:
        if isroom(data[7:-1]):
            move(client, data[7:-1])

        # If invalid room is entered give error and wait for new room
        else:
            server_message([client], "The door is locked\n")
    else:
        server_message([client], "You must enter a room name\n")


def stab(client, data):
    """ Function for executing the stab player command. Which makes a player start the game over. """
    if data[6:-1]:
        for victim in clients.itervalues():
            if victim.name == data[6:-1] and victim.room == client.room:
                send(client.name, victim, "Stabs you: Please enter a new name\n")
                broadcast(victim, "Server", "%s has been stabbed\n" % victim.name)

                victim.room.bodies += 1
                victim.room.poolofblood = True
                victim.room.removeoccupant(victim)
                victim.room = None
                victim.name = ""

                break
        else:
            server_message([client], "There is no %s in this room\n" % data[6:-1])
    else:
        server_message([client], "You must enter a name to stab\n")


def rc_quit(client, data):
    """ Function for executing the quit command. Which disconnects the client """
    client.clientsock.close()
    socket_list.remove(client.clientsock)
    client.room.removeoccupant(client)
    broadcast(client, "Server", "%s disappears in a puff of smoke\n" % client.name)
    del clients[client.clientsock]


def clean(client, data):
    """ Function for executing the clean command. Which removes blood from players room. """
    client.room.poolofblood = False
    broadcast(client, client.name, "cleans up the blood\n")


def hide(client, data):
    """ Function for executing the hide body command. Which removes a body from the players room. """
    if client.room.bodies > 0:
        client.room.bodies -= 1
        broadcast(client, client.name, "hides a body\n")
    else:
        client.room.bodies = 0


def look(client, data):
    """ Function for executing the look command. This command has two versions, one for looking at a room and one for
    looking at a player"""
    if len(data) > 6:
        lookplayer(client, data)
    else:
        lookroom(client)


def lookplayer(client, data):
    """ Function for executing the player part of the look command. Which gives the player a description of the player
    they are looking at"""
    for player in clients.itervalues():
        if player.name == data[6:-1] and player.room == client.room:
            server_message([client], "%s, %s\n" % (player.name, player.description))
            break
    else:
        server_message([client], "There is no %s here" % data[6:-1])


def lookroom(client):
    """ Function for executing the room part of the look command. Which gives the player a list of information about the
    room they are in. """
    otherrooms = list(rooms.iterkeys())
    otherrooms.remove(client.room.name)

    description = ("You are in the %s, %s\n" % (client.room.name, client.room.getdescription()) +
        "There are doors to the %s\n" % " and ".join(otherrooms) +
        listoccupants(client))

    server_message([client], description)


def hang(client, data):
    """ function for executing the hang art command. Which lets the player add some text the rooms description. """
    client.room.art = "%s" % data[6:26].rstrip()
    if client.room.art:
        broadcast(client, "Server", "%s hangs something on the wall\n" % client.name)
    else:
        server_message([client], "You must enter a description of the art\n")

def steal(client, data):
    """ function for executing the steal art command. Which lets the player remove the player added portion of the room
    Description. """
    client.room.art = ""
    broadcast(client, "Server", "%s takes something off the wall\n" % client.name)


def describeself(client, data):
    """ function for executing the describe command. Which lets the player change their description. """
    if data[10:30].rstrip():
        client.description = data[10:30].rstrip()
    else:
        server_message([client], "You must enter a description of yourself\n")


###################################
# Other functions
###################################
def move(client, room_to_enter):
    """ Move a user from one room to another """
    if client.room:
        client.room.removeoccupant(client)
        broadcast(client, "Server", "%s has left the room\n" % client.name)

    rooms[room_to_enter].addoccupant(client)
    client.room = rooms[room_to_enter]
    broadcast(client, "Server", "%s has entered the room\n" % client.name)

    server_message([client], listoccupants(client))


def isroom(s):
    """ Tests to see if a string is equivalent to a room name """
    if s in rooms:
        return True
    else:
        return False


def listoccupants(client):
    """ Send a list of room occupants """
    occupants = ""

    for c in clients.itervalues():
        if c.room == client.room and not c.name == client.name:
            occupants += "\n" + c.name

    if not occupants:
        return "The room is empty\n"
    else:
        return "The room contains: %s\n" % occupants


# Main function
if __name__ == "__main__":
    # Dictionary containing all the commands and functions they map too
    commands = {'help': rc_help, 'enter': enter, 'stab': stab, 'quit': rc_quit, 'look': look, 'clean': clean,
                'hide': hide, 'hang': hang, 'steal': steal, 'describe': describeself}

    # Dictionary containing all of the Room objects
    rooms = {}
    for room in config.rooms:
        rooms[room['name']] = Room(room['name'], room['description'])

    # List of all sockets
    socket_list = []

    # Dictionary of clients connected to the server
    clients = {}

    # List of names that are in use or have been killed
    names = config.names

    # Set up the server socket
    RECEIVE_BUFFER = 4096
    PORT = 5000  # The port which the application listens on
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind(("0.0.0.0", PORT))
    serversocket.listen(10)

    # Add the socket to the main list
    socket_list.append(serversocket)

    print "Chat server started on port " + str(PORT)

    # Listening loop
    while True:
        # Listen for a message and loop through all received messages
        read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
        for sock in read_sockets:

            # If the message is received on the server socket create a new connection
            if sock == serversocket:
                new_sock, address = serversocket.accept()
                clients[new_sock] = Client(address, new_sock)
                socket_list.append(new_sock)
                server_message([clients[new_sock]], 'Welcome to RogueChat: Please enter your name\n')

            # If the message is from an existing client check the content and user state
            else:
                try:
                    client = clients[sock]
                    data = sock.recv(RECEIVE_BUFFER)
                    if data:
                        print "data entered by " + str(sock)
                        print "%s" % data

                        # If the client has no name get its name and ask for room
                        if not client.name:
                            print "name entered"
                            if len(data) <= 25:
                                if data[:-1] in names:
                                    server_message([client], "That name is either in use or dead\n")
                                else:
                                    client.name = data[:-1]
                                    names.append(client.name)
                                    server_message([client], "You are in the Foyer. Enter #help for more information\n")
                                    move(client, "Foyer")
                            else:
                                server_message([client], "That name is too long\n")

                        # If the message is a command see which command it is
                        elif data[0] == '#':
                            print "command entered"
                            command = data.split(' ', 1)[0][1:].rstrip()
                            try:
                                commands[command](client, data)
                            except KeyError:
                                server_message([client], "Invalid command\n")

                        # Else send the message out to the rest of the users room
                        else:
                            print "message entered"
                            broadcast(client, client.name, data)

                # If a socket can't be communicated with remove it from the list and room
                except socket.error:
                    print "Client %s is offline\n" % sock
                    sock.close()
                    socket_list.remove(sock)
                    client.room.removeoccupant(client)
                    broadcast(client, "Server", "%s is offline\n" % client.name)
                    del clients[sock]
                    continue
                """
                except KeyError:
                    print "Client %s is offline\n" % sock
                    sock.close()
                    socket_list.remove(sock)
                """

    serversocket.close()