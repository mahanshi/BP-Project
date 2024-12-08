import socket
import errno
import sys
import time

HEADER_LENGTH = 10

IP = "localhost"
PORT = 8080
my_username = 'a'#input("Username: ")

# Create a socket
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to a given ip and port
client_socket.connect((IP, PORT))

# Set connection to non-blocking state, so .recv() call won't block, just return some exception we'll handle
client_socket.setblocking(False)

# Prepare username and header and send them
my_username = 'Hi Server!'
username = my_username.encode('utf-8')
username_header = (str(len(username)) + ' '*(HEADER_LENGTH-len(str(len(username))))).encode('utf-8')
client_socket.send(username_header + username)

def Json(s):
    return s


with open(sys.argv[1], 'r') as f:
    s = f.read()
print(s)
message = Json(s)
message = message.encode('utf-8')
message_header = (str(len(message)) + ' '*(HEADER_LENGTH-len(str(len(message))))).encode('utf-8')
client_socket.send(message_header + message)


while True:
    time.sleep(.5)
    try:
        # Now we want to loop over received messages (there might be more than one) and print them
        while True:

            # Receive our "header" containing username length, it's size is defined and constant
            message_header = client_socket.recv(HEADER_LENGTH)

            if not len(message_header):
                print('Connection closed by the server')
                sys.exit()

            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')

            if message == 'Done':
                pass
            else:
                username = message
                print('My Username for server: ', username)


    except IOError as e:
        # This is normal on non blocking connections - when there are no incoming data error is going to be raised
        # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
        # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
        # If we got different error code - something happened
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()

        # We just did not receive anything
        continue

    except Exception as e:
        # Any other exception - something happened, exit
        print('Reading error: {}'.format(str(e)))
        sys.exit()