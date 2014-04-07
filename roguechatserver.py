import socket
import select

import config
from objects import Room, Client

# Functions for sending messages


def broadcast(originclient, oname, message):
    """ Send a message to all occupants of a room """
    for sock in originclient.room.occupantslist:
        if sock != serversocket and sock != originclient.clientsock:
            try:
                output = "\r<%s> %s" % (oname, message)
                sock.getpeername()
                sock.send(output)
            except socket.error:
                print "Client %s is offline\n" % sock
                sock.close()
                originclient.room.removeoccupant(sock)
                socketlist.remove(sock)
                del clients[sock]


def send(originname, destclient, message):
    """ Send a message to one user """
    try:
        output = "\r<%s> %s" % (originname, message)
        destclient.clientsock.getpeername()
        destclient.clientsock.send(output)
    except socket.error:
        print "Client %s is offline\n" % destclient.name
        destclient.clientsock.close()
        destclient.room.removeoccupant(destclient.clientsock)
        socketlist.remove(destclient.clientsock)
        del clients[destclient.clientsock]

# Command functions


def rc_help(client, data):
    send("Server", client, config.helptext)


def enter(client, data):
    # if valid room is entered, enter room and list occupants
    if isroom(data[7:-1]):
        move(client, data[7:-1])

    # If invalid room is entered give error and wait for new room
    else:
        send("Server", client, "not a room\n")


def rc_stab(client, data):
    for victim in clients.itervalues():
        if victim.name == data[6:-1] and victim.room == client.room:
            send(client.name, victim, "Stabs you: Please enter a new name\n")
            broadcast(victim, "Server", "%s has been stabbed\n" % victim.name)

            victim.room.bodies += 1
            victim.room.poolofblood = True
            victim.room.removeoccupant(victim.clientsock)
            victim.room = None
            victim.name = ""

            break
    else:
        send("Server", client, "There is no %s in this room\n" % data[6:-1])


def rc_quit(client, data):
    sock.close()
    socketlist.remove(sock)
    client.room.removeoccupant(sock)
    broadcast(client, "Server", "%s disappears in a puff of smoke\n" % client.name)
    del clients[client.clientsock]


def clean(client, data):
    client.room.poolofblood = False
    broadcast(client, client.name, "cleans up the blood\n")


def hide(client, data):
    if client.room.bodies > 0:
        client.room.bodies -= 1
        broadcast(client, client.name, "hides a body\n")
    else:
        client.room.bodies = 0


def look(client, data):
    """ Give the player a list of information about the room they are in"""
    if len(data) > 6:
        lookplayer(client, data)
    else:
        lookroom(client)


def lookplayer(client, data):
    for player in clients.itervalues():
        if player.name == data[6:-1] and player.room == client.room:
            send("Server", client, "%s, %s\n" % (player.name, player.description))
            break
    else:
        send("Server", client, "There is no %s here" % data[6:-1])


def lookroom(client):
    otherrooms = list(rooms.iterkeys())
    otherrooms.remove(client.room.name)

    description = ("You are in the %s, %s\n" % (client.room.name, client.room.getdescription()) +
        "There are doors to the %s\n" % " and ".join(otherrooms) +
        listoccupants(client))

    send("Server", client, description)


def hang(client, data):
    client.room.art = "%s" % data[6:26].rstrip()
    broadcast(client, "Server", "%s hangs something on the wall\n" % client.name)


def steal(client, data):
    client.room.art = ""
    broadcast(client, "Server", "%s takes something off the wall\n" % client.name)


def describeself(client, data):
    client.description = data[10:31].rstrip()

# Other functions


def move(client, enter):
    """ Move a user from one room to another """

    if client.room:
        client.room.removeoccupant(client.clientsock)
        broadcast(client, "Server", "%s has left the room\n" % client.name)

    rooms[enter].addoccupant(client.clientsock)

    client.room = rooms[enter]
    broadcast(client, "Server", "%s has entered the room\n" % client.name)

    send("Server", client, listoccupants(client))


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
    commands = {'help': rc_help, 'enter': enter, 'stab': rc_stab, 'quit': rc_quit, 'look': look, 'clean': clean,
                'hide': hide, 'hang': hang, 'steal': steal, 'describe': describeself}

    # Dictionary containing all of the Room objects
    rooms = {}
    for room in config.rooms:
        rooms[room['name']] = Room(room['name'], room['description'])

    # List of all sockets
    socketlist = []

    # Dictionary of clients connected to the server
    clients = {}

    # List of names that are in use or have been killed
    names = config.names

    # Set up the server socket
    RECEIVE_BUFFER = 4096
    PORT = 5000 # The port which the application listens on
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind(("0.0.0.0", PORT))
    serversocket.listen(10)

    # Add the socket to the main list
    socketlist.append(serversocket)

    print "Chat server started on port " + str(PORT)

    # Listening loop
    while True:
        # Listen for a message and loop through all received messages
        readsockets, writesockets, errorsockets = select.select(socketlist,[],[])
        for sock in readsockets:

            # If the message is received on the server socket create a new connection
            if sock == serversocket:
                newsock, address = serversocket.accept()
                clients[newsock] = Client(address, newsock)
                socketlist.append(newsock)
                send("Server", clients[newsock], 'Welcome to RogueChat: Please enter your name\n')

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
                            if data[:-1] in names:
                                send("Server", client, "That name is either in use or dead\n")
                            else:
                                client.name = data[:-1]
                                names.append(client.name)
                                send("Server", client, "You are in the Foyer. Enter #help for more information\n")
                                move(client, "Foyer")

                        # If the message is a command see which command it is
                        elif data[0] == '#':
                            print "command entered"
                            command = data.split(' ', 1)[0][1:].rstrip()
                            print repr(command)
                            if command in commands:
                                commands[command](client, data)
                            else:
                                send("Server", client, "Invalid command\n")


                        # Else send the message out to the rest of the users room
                        else:
                            print "message entered"
                            broadcast(client, client.name, data)

                # If a socket can't be communicated with remove it from the list and room
                except socket.error:
                    print "Client %s is offline\n" % sock
                    sock.close()
                    socketlist.remove(sock)
                    client.room.removeoccupant(sock)
                    broadcast(client, "Server", "%s is offline\n" % client.name)
                    del clients[sock]

                    continue

    serversocket.close()