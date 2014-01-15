import socket
import select


# Send a message to all occupants of a room
def broadcast(origin, oname, message, room):
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


# Send a message to one user
def send(oname, destination, message):
    try:
        output = "\r<%s> %s" % (oname, message)
        destination.send(output)
    except socket.error:
        destination.close()
        lobby.remove(destination)


# Move a user from one room to another
def move(sock, leave, enter):
    enter.append(sock)
    leave.remove(sock)


# Remove a character and move user back to the lobby
def stab(killer, victimname):
    victim = nametosocket(victimname)
    send(killer, victim, "Stabs you: Please enter a new name\n")
    vclient = clients[victim.getpeername()]
    vroom = vclient[0]
    vclient[0] = "lobby"
    vclient[1] = ""
    rooms[vroom].remove(victim)


# Use a peer name to find the matching socket
def nametosocket(peername):
    sock = None
    print lobby

    for s in lobby:
        if not s == serversocket:
            print peername, s.getpeername()
            if peername == s.getpeername():
                sock = s
    return sock

def isroom(s):
    if s in rooms:
        return True
    else:
        return False


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
    PORT = 5000

    # Dictionary of clients
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
                clients[address] = ['lobby', '']
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
                        if not client[1]:
                            print "name entered"
                            if data[:-1] in names:
                                send("Server", sock, "That name is either in use or dead\n")
                            else:
                                client[1] = data[:-1]
                                names.append(client[1])
                                send("Server", sock, "choose a room " + str(rooms.keys()) + "\n")


                        # If the client has no room get its room and move it there
                        elif client[0] == "lobby":
                            print "room entered"

                            # if valid room is entered, enter room and list occupants
                            if isroom(data[:-1]):
                                client[0] = data[:-1]
                                rooms[client[0]].append(sock)
                                broadcast(sock, "Server", "%s has entered the room\n" % client[1], client[0])

                                occupants = ''
                                for c in clients.itervalues():
                                    print c
                                    if c[0] == client[0]:
                                        occupants += '\n' + c[1]

                                send("Server", sock, "room contains: %s\n" % occupants)

                            # if invalid room is enter give error and wait for new room
                            else:
                                send("Server", sock, "not a room\n")




                        # If the message is a command see which command it is
                        elif data[0] == '#':
                            print "command entered"

                            # If the command was enter move the user to a different room
                            if data[1:6] == "enter":

                                # if valid room is entered, enter room and list occupants
                                if isroom(data[7:-1]):
                                    print rooms[client[0]], rooms[data[7:-1]]
                                    move(sock, rooms[client[0]], rooms[data[7:-1]])
                                    print rooms[client[0]], rooms[data[7:-1]]

                                    broadcast(sock, "Server", "%s has left the room\n" % client[1], client[0])
                                    client[0] = data[7:-1]
                                    broadcast(sock, "Server", "%s has entered the room\n" % client[1], client[0])

                                    occupants = ''
                                    for c in clients.itervalues():
                                        print c
                                        if c[0] == client[0]:
                                            occupants += '\n' + c[1]

                                    send("Server", sock, "room contains: %s\n" % occupants)

                                 # if invalid room is enter give error and wait for new room
                                else:
                                    send("Server", sock, "not a room\n")

                            # If the command is leave move the user back to the lobby
                            elif data[1:6] == "leave":
                                rooms[client[0]].remove(sock)
                                client[0] = "lobby"
                                send("Server", sock, "choose a room " + str(rooms.keys()) + "\n")

                            # If the command is stab remove the stabbed character from the game
                            elif data[1:6] == "stab ":
                                for k, c in clients.iteritems():
                                    print k, c, data[6:-1]
                                    if c[1] == data[6:-1]:
                                        print "stab 2"
                                        stab(client[1], k)

                            elif data[1:5] == "quit":
                                sock.close()
                                lobby.remove(sock)
                                rooms[client[0]].remove(sock)


                        # Else send the message out to the rest of the users room
                        else:
                            print "message entered"
                            broadcast(sock, client[1], data, client[0])

                # If a socket can't be communicated with remove it from the list and room
                except socket.error:
                    print "error"
                    broadcast(sock, "Server", "%s is offline\n" % client[1], client[0])
                    print "Client (%s, %s) is offline\n" % (address[0], address[1])
                    sock.close()
                    lobby.remove(sock)
                    rooms[client[0]].remove(sock)
                    continue

    serversocket.close()