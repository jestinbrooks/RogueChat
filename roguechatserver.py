import socket
import select


class Client:
    """ An object containing a clients name, location, and address """
    def __init__(self, add, sock):
        self.room = "Foyer"
        self.name = ""
        self.address = add
        self.clientsock = sock


def broadcast(origin, oname, message, room):
    """ Send a message to all occupants of a room """
    roomlist = rooms[room]

    for sock in roomlist:
        if sock != serversocket and sock != origin:
            try:
                output = "\r<%s> %s" % (oname, message)
                sock.send(output)
            except socket.error:
                sock.close()
                rooms[room].remove(sock)
                lobby.remove(sock)


def send(oname, destination, message):
    """ Send a message to one user """
    try:
        output = "\r<%s> %s" % (oname, message)
        destination.send(output)
    except socket.error:
        destination.close()
        lobby.remove(destination)


def move(sock, leave, enter):
    """ Move a user from one room to another """
    rooms[enter].append(sock)
    if leave:
        leave.remove(sock)
        broadcast(sock, "Server", "%s has left the room\n" % client.name, client.room)

    client.room = enter
    broadcast(sock, "Server", "%s has entered the room\n" % client.name, client.room)

    listoccupants(client, sock)


def stab(killer, victimname):
    """ Remove a character and move user back to the lobby """
    victim = clients[victimname].clientsock
    send(killer, victim, "Stabs you: Please enter a new name\n")
    vclient = clients[victim.getpeername()]
    vroom = vclient.room
    vclient.room = "lobby"
    vclient.name = ""
    rooms[vroom].remove(victim)


def isroom(s):
    """ tests to see if a string is equivalent to a room name """
    if s in rooms:
        return True
    else:
        return False


def listoccupants(client, sock):
    """ Send a list of room occupants """
    occupants = ""

    for c in clients.itervalues():
        if c.room == client.room and not c.name == client.name:
            occupants += "\n" + c.name

    if not occupants:
        send("Server", sock, "The room is empty\n")
    else:
        send("Server", sock, "The room contains: %s\n" % occupants)


# Main function
if __name__ == "__main__":
    # List of all sockets
    lobby = []

    # Lists of sockets for each room and a dictionary containing all of the lists
    foyer = []
    drawingroom = []
    dininghall = []
    rooms = {"Foyer": foyer, "Drawing Room": drawingroom, "Dining Hall": dininghall}

    RECV_BUFFER = 4096
    # The port which the application listens on
    PORT = 5000

    # Dictionary of clients connected to the server
    clients = {}

    # List of names that are in use or have been killed
    names = ['Server', 'server']

    # Create and bind a socket for listening on
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind(("0.0.0.0", PORT))
    serversocket.listen(10)

    # Add the socket to the main list
    lobby.append(serversocket)

    print "Chat server started on port " + str(PORT)

    # Listening loop
    while True:
        # Listen for a message and loop through all received messages
        readsockets,writesockets,errorsockets = select.select(lobby,[],[])
        for sock in readsockets:

            # If the message is received on the server socket create a new connection
            if sock == serversocket:
                newsock, address = serversocket.accept()
                print type(address)
                clients[address] = Client(address, newsock)
                lobby.append(newsock)
                send("Server", newsock, 'Welcome to RogueChat: Please enter your name\n')

            # If the message is from an existing client check the content and user state
            else:
                try:
                    client = clients[sock.getpeername()]
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        print "data entered by" + str(sock.getpeername())
                        print "%s" % data

                        # If the client has no name get its name and ask for room
                        if not client.name:
                            print "name entered"
                            if data[:-1] in names:
                                send("Server", sock, "That name is either in use or dead\n")
                            else:
                                client.name = data[:-1]
                                names.append(client.name)
                                send("Server", sock, "You are in the Foyer\n")
                                move(sock, "", "Foyer")

                        # If the message is a command see which command it is
                        elif data[0] == '#':
                            print "command entered"

                            # If the command was enter move the user to a different room
                            if data[1:6] == "enter":
                                # if valid room is entered, enter room and list occupants
                                if isroom(data[7:-1]):
                                    move(sock, rooms[client.room], data[7:-1])

                                # If invalid room is enter give error and wait for new room
                                else:
                                    send("Server", sock, "not a room\n")

                            # If the command is leave move the user back to the lobby
                            elif data[1:6] == "leave":
                                rooms[client.room].remove(sock)
                                client.room = "lobby"
                                send("Server", sock, "choose a room " + str(rooms.keys()) + "\n")

                            # If the command is stab remove the stabbed character from the game
                            elif data[1:6] == "stab ":
                                for k, c in clients.iteritems():
                                    print k, c, data[6:-1]
                                    if c.name == data[6:-1]:
                                        print "stab 2"
                                        stab(client.name, k)

                            elif data[1:5] == "quit":
                                sock.close()
                                lobby.remove(sock)
                                rooms[client.room].remove(sock)

                        # Else send the message out to the rest of the users room
                        else:
                            print "message entered"
                            broadcast(sock, client.name, data, client.room)

                # If a socket can't be communicated with remove it from the list and room
                except socket.error:
                    print "error"
                    broadcast(sock, "Server", "%s is offline\n" % client.name, client.room)
                    print "Client (%s, %s) is offline\n" % (address[0], address[1])
                    sock.close()
                    lobby.remove(sock)
                    rooms[client.room].remove(sock)
                    continue

    serversocket.close()