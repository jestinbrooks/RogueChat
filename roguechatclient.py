import socket
import select
import sys


# Creates the input prompt
def prompt():
    sys.stdout.write('<You> ')
    sys.stdout.flush()


# Main function
if __name__ == "__main__":

    try:
        host = sys.argv[1]
    except IndexError:
        host = "localhost"

    # Server connection information
    #host = 'localhost'
    port = 5000

    # Create socket to connect to server
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.settimeout(2)

    # Attempt to connect to server
    try:
        clientsocket.connect((host, port))
    except socket.error:
        print 'Unable to connect'
        sys.exit()

    # Listening for input or message from server
    while True:
        sockets = [sys.stdin, clientsocket]

        # Listen for input or a message and loop through all received messages
        read_sockets, write_sockets, error_sockets = select.select(sockets, [], [])
        for sock in read_sockets:

            # If the message is from the server check if there is any data and then print
            if sock == clientsocket:
                data = sock.recv(4096)
                if not data:
                    print '\nDisconnected from chat server'
                    sys.exit()
                # Print messages from the server
                else:
                    sys.stdout.write(data)
                    prompt()

            # If message is from input send to the server
            else:
                message = sys.stdin.readline()
                clientsocket.send(message)
                prompt()