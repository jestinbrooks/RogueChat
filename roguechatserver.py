import socket
import select

import config
from objects import Room, Client


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


def move(client, enter):
    """ Move a user from one room to another """

    if client.room:
        client.room.removeoccupant(client.clientsock)
        broadcast(client, "Server", "%s has left the room\n" % client.name)

    rooms[enter].addoccupant(client.clientsock)

    client.room = rooms[enter]
    broadcast(client, "Server", "%s has entered the room\n" % client.name)

    send("Server", client, listoccupants(client))


def stab(killer, victimadd):
    """ Remove a character and move user back to entering a name """
    victim = clients[victimadd]
    send(killer, victim, "Stabs you: Please enter a new name\n")
    broadcast(victim, "Server", "%s has been stabbed\n" % victim.name)
    
    # reset victim and remove from room
    vroom = victim.room
    vroom.bodies += 1
    vroom.poolofblood = True
    victim.room = None
    victim.name = ""
    vroom.removeoccupant(victim.clientsock)


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


def look(client):
    """ Give the player a list of information about the room they are in"""
    otherrooms = list(rooms.iterkeys())
    otherrooms.remove(client.room.name)

    description = "You are in the %s, %s\n" % (client.room.name, client.room.getdescription()) + \
        "There are doors to the %s\n" % " and ".join(otherrooms) + \
        listoccupants(client)

    send("Server", client, description)

# Main function
if __name__ == "__main__":
    # List of all sockets
    socketlist = []

    # Lists of sockets for each room and a dictionary containing all of the lists
    rooms = {}
    for room in config.rooms:
        rooms[room['name']] = Room(room['name'], room['description'])

    RECV_BUFFER = 4096
    # The port which the application listens on
    PORT = 5000

    # Dictionary of clients connected to the server
    clients = {}

    # List of names that are in use or have been killed
    names = config.names

    # Create and bind a socket for listening on
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
                #print type(address)
                clients[newsock] = Client(address, newsock)
                socketlist.append(newsock)
                send("Server", clients[newsock], 'Welcome to RogueChat: Please enter your name\n')

            # If the message is from an existing client check the content and user state
            else:
                try:
                    client = clients[sock]
                    data = sock.recv(RECV_BUFFER)
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

                            # If the command was enter move the user to a different room
                            if data[1:6] == "enter":
                                # if valid room is entered, enter room and list occupants
                                if isroom(data[7:-1]):
                                    move(client, data[7:-1])

                                # If invalid room is enter give error and wait for new room
                                else:
                                    send("Server", client, "not a room\n")

                            # If the command is stab remove the stabbed character from the game
                            elif data[1:6] == "stab ":
                                for c in clients.itervalues():
                                    if c.name == data[6:-1] and c.room == client.room:
                                        stab(client.name, c.clientsock)
                                        break
                                else:
                                    send("Server", client, "There is no %s in this room\n" % data[6:-1])

                            elif data[1:5] == "quit":
                                sock.close()
                                socketlist.remove(sock)
                                client.room.removeoccupant(sock)
                                broadcast(client, "Server", "%s disappears in a puff of smoke\n" % client.name)
                                del clients[client.clientsock]

                            elif data[1:5] == "look":
                                look(client)

                            elif data[1:6] == "clean":
                                client.room.poolofblood = False
                                broadcast(client, client.name, "cleans up the blood\n")

                            elif data[1:10] == "hide body":
                                if client.room.bodies > 0:
                                    client.room.bodies -= 1
                                    broadcast(client, client.name, "hides a body\n")
                                else:
                                    client.room.bodies = 0

                            elif data[1:5] == "hang":
                                client.room.art = "%s" % data[6:26].rstrip()
                                broadcast(client, "Server", "%s hangs something on the wall\n" % client.name)

                            elif data[1:10] == "steal art":
                                client.room.art = ""
                                broadcast(client, "Server", "%s takes something off the wall\n" % client.name)

                            elif data[1:5] == "help":
                                send("Server", client, config.helptext)

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