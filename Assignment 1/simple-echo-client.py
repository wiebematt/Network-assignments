# This example is using Python 2.7
import socket

# Specify server name and port number to connect to.
#
# API: gethostname()
#   returns a string containing the hostname of the
#   machine where the Python interpreter is currently
#   executing.
server_name = socket.gethostname()
print 'Hostname: ', server_name
server_port = 8181

# Make a TCP socket object.
#
# API: socket(address_family, socket_type)
#
# Address family
#   AF_INET: IPv4
#   AF_INET6: IPv6
#
# Socket type
#   SOCK_STREAM: TCP socket
#   SOCK_DGRAM: UDP socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to server machine and port.
#
# API: connect(address)
#   connect to a remote socket at the given address.
s.connect((server_name, server_port))
print 'Connected to server ', server_name

# messages to send to server.
mutable_bytes = [2, 4, "3+12", 6, "1+12/3"]

# Send messages to server over socket.
#
# API: send(string)
#   Sends data to the connected remote socket.
#   Returns the number of bytes sent. Applications
#   are responsible for checking that all data
#   has been sent
#
# API: recv(bufsize)
#   Receive data from the socket. The return value is
#   a string representing the data received. The
#   maximum amount of data to be received at once is
#   specified by bufsize
#
# API: sendall(string)
#   Sends data to the connected remote socket.
#   This method continues to send data from string
#   until either all data has been sent or an error
#   occurs.
bufsize = 16
for line in mutable_bytes:
    if type(line) is int:
        s.send(str(socket.htons(line)))
    else:
        s.send(line)
data = s.recv(bufsize)
print 'Client received: ', repr(data)  # Close socket to send EOF to server.
s.close()
