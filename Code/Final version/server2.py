
import socket
import select
from queue import Queue
import time
import threading
import json
import json_to_img


q = Queue()

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
work = {}
finish = {}

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


def close_connection(notified_socket):
    print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

    # Remove from list for socket.socket()
    sockets_list.remove(notified_socket)

    # Remove from our list of users
    del clients[notified_socket]
    del work[notified_socket]
    del finish[notified_socket]


def json_to_pic(s, w, j):
    #o = threading.Lock()
    #o.acquire()
    time.sleep(3)
    #print(s)
    s = json.loads(s)
    try:
        json_to_img.main(s, j)
    except:
        message = "Color out of bound"
        message = message.encode('utf-8')
        message_header = (str(len(message)) + ' ' * (HEADER_LENGTH - len(str(len(message))))).encode(
            'utf-8')
        w.send(message_header + message)
        finish[w] = 1
    #o.release()
    finish[w] = 1

print_lock = threading.Lock()


def threader():
    while True:
        job = q.get()
        if job > 0:
            done_flag = 1
            while done_flag:
                time.sleep(.1)
                l = threading.Lock()
                l.acquire()
                try:
                    for job in range(1, 11):
                        for c in clients:
                            #print(clients[c], job)
                            if clients[c]['data'].decode('utf-8') == str(job) and finish[c] == 0:
                                #print(job, clients[c]['data'])
                                json_to_pic(work[c], c, str(job))
                                #q.task_done()
                                done_flag = 0

                except:
                    pass
                finally:
                    l.release()
        else:
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
                        finish[client_socket] = 0
                        clients[client_socket] = user

                        print('Accepted new connection from ', *client_address, 'username: ', user['data'].decode('utf-8'))

                    # Else existing socket is sending a message
                    else:

                        # Receive message
                        message = receive_message(notified_socket)

                        # If False, client disconnected, cleanup
                        if message is False:
                            close_connection(notified_socket)
                            continue
                        if message['data'].decode('utf-8') == 'waiting...':
                            if finish[notified_socket] == 0:
                                continue
                            ml = threading.Lock()
                            ml.acquire()
                            message = "Done"
                            message = message.encode('utf-8')
                            message_header = (str(len(message)) + ' ' * (HEADER_LENGTH - len(str(len(message))))).encode(
                                'utf-8')
                            notified_socket.send(message_header + message)
                            # SENDING IMAGE
                            #print(notified_socket, threading.current_thread())
                            close_connection(notified_socket)
                            ml.release()
                            continue

                        # Get user by notified socket, so we will know who sent the message
                        #l = threading.Lock()
                        #l.acquire()
                        user = clients[notified_socket]
                        work[notified_socket] = message["data"].decode("utf-8")
                        client_socket = notified_socket
                        #print('Received message from ', user["data"].decode("utf-8"), ':', message["data"].decode("utf-8"))

                        # Sending Username of client
                        message = str(sockets_list.index(client_socket))
                        message = message.encode('utf-8')
                        message_header = (str(len(message)) + ' ' * (HEADER_LENGTH - len(str(len(message))))).encode('utf-8')
                        client_socket.send(message_header + message)

                for notified_socket in exception_sockets:

                    # Remove from list for socket.socket()
                    sockets_list.remove(notified_socket)

                    # Remove from our list of users
                    del clients[notified_socket]

for i in range(2):
    t = threading.Thread(target=threader)
    t.daemon = True
    t.start()
for i in range(11):
    q.put(i)
q.join()
