# This example is using Python 2.7
import socket
import thread

# Get host name, IP address, and port number.
import sys

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
    first = connect.recv(bufsize)
    second = connect.recv(bufsize)
    # third = connect.recv(bufsize)
    conn.send('First => ' + first + " " + str(sys.getsizeof(first)))
    conn.send('Second => ' + second + " " + str(sys.getsizeof(second)))
    # conn.send('Second => ' + third + " " + str(sys.getsizeof(third)))
    # number_of_expressions = socket.ntohs(int(connect.recv(bufsize)))
    # for count in range(0, number_of_expressions):
    #     bytes_sent = conn.send('Echo => ' + str(count))
    #     print bytes_sent


def math_handler(input):
    pass


while True:
    conn, addr = s.accept()
    print 'Server connected by', addr
    thread.start_new(handler, (conn,))
