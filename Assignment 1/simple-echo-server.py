# This example is using Python 2.7
import socket

# Get host name, IP address, and port number.
#
# API: gethostname()
#   returns a string containing the hostname of the
#   machine where the Python interpreter is currently
#   executing.
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
host_port = 8181

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

# Bind to server IP and port number.
#
# API: bind(address)
#   Bind the socke to address.
s.bind((host_ip, host_port))

# Listen allow 5 pending connects.
#
# API: listen(backlog)
#   Listen for connections made to the socket. The
#   backlog argument specifies the maximum number
#   of queued connections
s.listen(5)

print 'Server started. Waiting for connection...'

# Listen until process is killed.
#
# API: accept()
#   Accept an incoming connection. The return value
#   is a pair (conn, address) where conn is a new socket
#   object usable to send and receive data on the
#   connection, and address is the address bound to the
#   socket on the other end of the connection.
bufsize = 16
while True:
    # Wait for next client connect.
    conn, addr = s.accept()
    print 'Server connected by ', addr

    # Read next line on client socket. Send a reply line to the client
    # until EOF when socket closed.
    while True:
        data = conn.recv(bufsize)
        if not data: break
        print 'Server received: ', repr(data)
        conn.send('Echo => ' + data)

    # Close TCP connection.
    conn.close()
