# This example is using Python 2.7
import socket
import thread
import time

# Get host name, IP address, and port number.
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
host_port = 8181

# Make a TCP socket object.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind to server IP and port number.
s.bind((host_ip, host_port))

# Listen allow 5 pending connects.
s.listen(5)

bufsize = 16


# Handle first read

def handler(connect):
    expressions = ""
    while True:
        next_byte = connect.recv(bufsize)
        if not next_byte:
            break
        expressions += next_byte
    print expressions
    connect.sendall('Echo ==> ' + expressions)
    connect.close()


while True:
    conn, addr = s.accept()
    print 'Server connected by', addr
    thread.start_new(handler, (conn,))
