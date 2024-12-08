#!/usr/bin/python3

import socket
import select

HEADER_LENGTH = 10

IP = "localhost"
PORT = 8080

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# SO_ - socket option
# SOL_ - socket option level
# Sets REUSEADDR (as a socket option) to 1 on socket
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))
server_socket.listen(10)

sockets_list = [server_socket]

# List of connected clients - socket as a key, user header and name as data
clients = {}

print('Listening for connections on ', IP, ' ', str(PORT))

#  ####################################################################################################


# Handles message receiving
def receive_message(client_socket):

    try:

        # Receive our "header" containing message length, it's size is defined and constant
        message_header = client_socket.recv(HEADER_LENGTH)

        # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(message_header):
            return False

        # Convert header to int value
        message_length = int(message_header.decode('utf-8').strip())
        # Return an object of message header and message data
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        print('here')
        # If we are here, client closed connection violently, for example by pressing ctrl+c on his script
        # or just lost his connection
        # socket.close() also invokes socket.shutdown(socket.SHUT_RDWR) what sends information about closing the socket (shutdown read/write)
        # and that's also a cause when we receive an empty message
        return False

while True:

    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    # Iterate over notified sockets
    for notified_socket in read_sockets:

        # If notified socket is a server socket - new connection, accept it
        if notified_socket == server_socket:

            client_socket, client_address = server_socket.accept()

            message = str(len(sockets_list))
            message = message.encode('utf-8')
            message_header = (str(len(message)) + ' ' * (HEADER_LENGTH - len(str(len(message))))).encode('utf-8')
            user = {'header': message_header, 'data': message}

            sockets_list.append(client_socket)

            clients[client_socket] = user

            print('Accepted new connection from ', *client_address, 'username: ', user['data'].decode('utf-8'))

        # Else existing socket is sending a message
        else:

            # Receive message
            message = receive_message(notified_socket)

            # If False, client disconnected, cleanup
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                # Remove from list for socket.socket()
                sockets_list.remove(notified_socket)

                # Remove from our list of users
                del clients[notified_socket]

                continue

            # Get user by notified socket, so we will know who sent the message
            user = clients[notified_socket]
            client_socket = notified_socket
            print('Received message from ', user["data"].decode("utf-8"), ':', message["data"].decode("utf-8"))
            # Sending Username of client
            message = str(sockets_list.index(client_socket))
            message = message.encode('utf-8')
            message_header = (str(len(message)) + ' ' * (HEADER_LENGTH - len(str(len(message))))).encode('utf-8')
            client_socket.send(message_header + message)

    # It's not really necessary to have this, but will handle some socket exceptions just in case
    for notified_socket in exception_sockets:

        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

        # Remove from our list of users
        del clients[notified_socket]