import socket, json, threading
from queue import Queue

q = Queue()

all_connections = []
all_address = []
host, port, s = 0, 0, 0
data = []


def new_conn():
    for c in all_connections:
        c.close()

    del all_connections[:]
    del all_address[:]
    #vis = []
    while True:
        #try:
            conn, address = s.accept()
            s.setblocking(1)  # prevents timeout

            all_connections.append(conn)
            all_address.append(address)
            print("Connection has been established :" + address[0])


            s.sendall('1'.encode())
            data.append(s.recv(1024).decode())


        #except:
         #   print("Error accepting connections")


def create_socket():
    try:
        global host
        global port
        global s
        host = "localhost"
        port = 8080
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    except socket.error as msg:
        print("Socket creation error: " + str(msg))


def bind_socket():
    try:
        global host
        global port
        global s
        print("Binding the Port: " + str(port))

        s.bind((host, port))
        s.listen(5)

    except socket.error as msg:
        print("Socket Binding error" + str(msg) + "\n" + "Retrying...")
        bind_socket()


def create_image(s):
    pass


def work():
    while True:
        x = q.get()
        print(q)
        if x == 0:  # new client
            create_socket()
            bind_socket()
            new_conn()

            tn = threading.Thread(target=work)
            tn.daemon = True
            tn.start()
            q.put(len(all_connections))
            q.join()

        else:
            create_image(data[x])
        q.task_done()


t1 = threading.Thread(target=work)
t1.daemon = True
t1.start()
q.put(0)
q.join()
