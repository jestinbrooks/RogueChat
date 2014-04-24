import socket
import select

import config
from objects import Room, Client


#######################################
# Functions for sending messages
#######################################
def broadcast(origin_client, origin_name, message):
    """ Send a message to all occupants of a room """
    full_message = "\r<%s> %s" % (origin_name, message)
    for client in origin_client.room.occupants_list:
        if client.clientsock != origin_client.clientsock:
            try:
                client.clientsock.getpeername()
                client.clientsock.send(full_message)
            except socket.error:
                print "Client %s is offline-Broadcast\n" % client.name
                client.clientsock.close()
                client.room.occupants_list.remove(client)
                server_message(client.room.occupants_list, "%s disappears in a puff of smoke\n" % client.name)
                socket_list.remove(client.clientsock)
                del clients[client.clientsock]


def send(origin_client, destination_client, message):
    """ Send a message to one user """
    full_message = "\r<%s> %s" % (origin_client.name, message)
    try:
        destination_client.clientsock.getpeername()
        destination_client.clientsock.send(full_message)
    except socket.error:
        print "Client %s is offline-Send\n" % destination_client.name
        destination_client.clientsock.close()
        destination_client.room.occupants_list.remove(destination_client)
        server_message(client.room.occupants_list, "%s disappears in a puff of smoke\n" % client.name)
        socket_list.remove(destination_client.clientsock)
        del clients[destination_client.clientsock]


def server_message(client_list, message):
    """ Send a message from the server to a list of clients """
    full_message = "\r%s" % message
    for client in client_list:
        try:
            client.clientsock.getpeername()
            client.clientsock.send(full_message)
        except socket.error:
            print "Client %s is offline-Server message\n" % client.name
            client.clientsock.close()
            client.room.occupants_list.remove(client)
            server_message(client.room.occupants_list, "%s disappears in a puff of smoke\n" % client.name)
            socket_list.remove(client.clientsock)
            del clients[client.clientsock]


############################
# Command functions
############################
def rc_help(client, data):
    """ Function for executing the help command. Which gives a list of commands. """
    server_message([client], config.help_text)


def enter(client, data):
    """ Function for executing the enter command. Which moves the player to a new room. """
    # if valid room is entered, enter room and list occupants
    if data[7:-1]:
        if is_room(data[7:-1]):
            move(client, data[7:-1])
        # If invalid room is entered give error and wait for new room
        else:
            server_message([client], "The door is locked\n")
    else:
        server_message([client], "You must enter a room name\n")


def stab(client, data):
    """ Function for executing the stab player command. Which makes a player start the game over. """
    if data[6:-1]:
        for victim in client.room.occupants_list:
            if victim.name == data[6:-1]:
                send(client, victim, "Stabs you: Please enter a new name\n")
                victim.room.stabbed(victim)
                server_message(client.room.occupants_list, "%s has been stabbed\n" % victim.name)
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
    client.room.occupants_list.remove(client)
    server_message(client.room.occupants_list, "%s disappears in a puff of smoke\n" % client.name)
    del clients[client.clientsock]


def clean(client, data):
    """ Function for executing the clean command. Which removes blood from players room. """
    if client.room.poolofblood:
        client.room.poolofblood = False
        broadcast(client, client.name, "cleans up the blood\n")
    else:
        broadcast(client, client.name, "cleans up the room\n")


def hide(client, data):
    """ Function for executing the hide body command. Which removes a body from the players room. """
    if data[6:-1] == "body" and client.room.bodies > 0:
            client.room.bodies -= 1
            broadcast(client, client.name, "hides a body\n")
    else:
        server_message([client], "You can't hide that\n")
        client.room.bodies = 0


def look(client, data):
    """ Function for executing the look command. This command has two versions, one for looking at a room and one for
    looking at a player"""
    if len(data) > 6:
        look_player(client, data)
    else:
        look_room(client)


def look_player(client, data):
    """ Function for executing the player part of the look command. Which gives the player a description of the player
    they are looking at"""
    for player in clients.itervalues():
        if player.name == data[6:-1] and player.room == client.room:
            server_message([client], "%s, %s\n" % (player.name, player.description))
            break
    else:
        server_message([client], "There is no %s here" % data[6:-1])


def look_room(client):
    """ Function for executing the room part of the look command. Which gives the player a list of information about the
    room they are in. """
    other_rooms = list(rooms.iterkeys())
    other_rooms.remove(client.room.name)
    description = ("You are in the %s, %s\n" % (client.room.name, client.room.get_description()) +
        "There are doors to the %s\n" % " and ".join(other_rooms) +
        list_occupants(client))
    server_message([client], description)


def hang(client, data):
    """ function for executing the hang art command. Which lets the player add some text the rooms description. """
    client.room.art = "%s" % data[6:26].rstrip()
    if client.room.art:
        server_message(other_occupants(client), "%s hangs something on the wall\n" % client.name)
    else:
        server_message([client], "You must enter a description of the art\n")


def steal(client, data):
    """ function for executing the steal art command. Which lets the player remove the player added portion of the room
    Description. """
    if data[7:-1] == "art" and client.room.art:
            client.room.art = ""
            server_message(other_occupants(client), "%s takes something off the wall\n" % client.name)
    else:
        server_message([client], "You can't steal that\n")



def describe_self(client, data):
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
        client.room.occupants_list.remove(client)
        server_message(client.room.occupants_list, "%s has left the room\n" % client.name)
    client.room = rooms[room_to_enter]
    server_message(client.room.occupants_list, "%s has entered the room\n" % client.name)
    rooms[room_to_enter].occupants_list.append(client)
    server_message([client], list_occupants(client))


def is_room(s):
    """ Tests to see if a string is equivalent to a room name """
    if s in rooms:
        return True
    else:
        return False


def list_occupants(client):
    """ Send a list of room occupants """
    occupants = [c.name for c in client.room.occupants_list if not c is client]
    if not occupants:
        return "The room is empty\n"
    else:
        return "The room contains: %s\n" % ", ".join(occupants)


def other_occupants(client):
    occupants = list(client.room.occupants_list)
    occupants.remove(client)
    if occupants:
        return occupants
    else:
        return []


##########################
# Main function
##########################
if __name__ == "__main__":
    commands = {'help': rc_help, 'enter': enter, 'stab': stab, 'quit': rc_quit, 'look': look, 'clean': clean,
                'hide': hide, 'hang': hang, 'steal': steal, 'describe': describe_self}
    rooms = {room['name']: Room(room['name'], room['description']) for room in config.rooms}
    socket_list = []  # create an empty list to store all sockets in
    clients = {}  # create an empty dictionary to store all the clients connected to the server
    names = set(config.names)  # Set of names that are in use or have been killed

    # Set up the server socket
    RECEIVE_BUFFER = 4096
    PORT = 5000  # The port which the application listens on
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)
    socket_list.append(server_socket)
    print "Chat server started on port " + str(PORT)

    # Listening loop
    while True:
        # Listen for a message and loop through all received messages
        read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
        for connection in read_sockets:
            # If the message is received on the server socket create a new connection
            if connection == server_socket:
                new_connection, address = server_socket.accept()
                clients[new_connection] = Client(address, new_connection)
                socket_list.append(new_connection)
                server_message([clients[new_connection]], 'Welcome to RogueChat: Please enter your name\n')
            # If the message is from an existing client check the content and user state
            else:
                try:
                    client = clients[connection]
                    data = connection.recv(RECEIVE_BUFFER)
                # If a socket can't be communicated with remove it from the list and room
                except socket.error:
                    print "Client %s is offline-Main loop\n" % connection
                    connection.close()
                    socket_list.remove(connection)
                    client.room.occupants_list.remove(client)
                    server_message(client.room.occupants_list, "%s disappears in a puff of smoke\n" % client.name)
                    del clients[connection]
                    continue
                # If data is received from a
                except KeyError:
                    continue
                if data:
                    print "%s entered by %s" % (data, str(connection))
                    # If the client has no name get its name and ask for room
                    if not client.name:
                        print "name entered"
                        if len(data) <= 25:
                            if data[:-1] in names:
                                server_message([client], "That name is either in use or dead\n")
                            else:
                                client.name = data[:-1]
                                names.add(client.name)
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
    server_socket.close()