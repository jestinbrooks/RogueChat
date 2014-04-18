import socket
import select
import sys


# Creates the input prompt
def prompt():
    sys.stdout.write('<You> ')
    sys.stdout.flush()


# Main function
if __name__ == "__main__":

    # Server connection information
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = "localhost"

    port = 5000

    # Create socket to connect to server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(2)

    # Attempt to connect to server
    try:
        client_socket.connect((host, port))
    except socket.error:
        print 'Unable to connect'
        sys.exit()

    # Listening for input or message from server
    while True:
        sockets = [sys.stdin, client_socket]

        # Listen for input or a message and loop through all received messages
        read_sockets, write_sockets, error_sockets = select.select(sockets, [], [])
        for sock in read_sockets:

            # If the message is from the server check if there is any data and then print
            if sock == client_socket:
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
                client_socket.send(message)
                prompt()