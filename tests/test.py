import socket
import threading

HOST = "127.0.0.1"
PORT = 8888
BUFFER_SIZE = 1024

# create a TCP/IP socket server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind socket
sock.bind((HOST, PORT))
# listen for incoming connections
sock.listen(5)

connections = {}
data_lock = threading.Lock()

def send_message_to_addr(addr, message):
    conn = connections[addr]
    conn.sendall("Hello from server".encode())

def handle_current_connection(conn, addr):
    while True:
        # receive data
        data = conn.recv(BUFFER_SIZE)
        if not data:
            continue
        elif data == "close":
            print("Connection from {} closed".format(addr))
            # remove connection from selector
            connections.pop(addr)
        else:
            # process data
            print("Received data: {} from {}".format(data, addr))
            # send data to all connections
            for(addr, conn) in connections.items():
                send_message_to_addr(addr, "TESTING")

while True:
    data_lock.acquire()
    # accept connection
    conn, addr = sock.accept()
    # add connection to list of connections
    connections[addr] = conn
    print("Connection from {}".format(addr))
    data_lock.release()

    # handle current connection
    new_thread = threading.Thread(target=handle_current_connection, args=(conn, addr))
    new_thread.start()