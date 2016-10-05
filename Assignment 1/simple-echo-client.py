# This example is using Python 2.7
import socket
import struct

# Specify server name and port number to connect to.
#
# API: gethostname()
#   returns a string containing the hostname of the
#   machine where the Python interpreter is currently
#   executing.
# server_name = socket.gethostname()
# print 'Hostname: ', server_name
# server_port = 8181
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect((server_name, server_port))
# print 'Connected to server ', server_name
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

# Connect to server machine and port.
#
# API: connect(address)
#   connect to a remote socket at the given address.


# messages to send to server.
# mutable_bytes = [3, 10, "100*10/5-2", 10, "40/2*20+20", 11, "1000+1000*2"]


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

def package_data(expressions):
    """ Take a"""
    return_package = ""
    num_packer = struct.Struct('H')
    for DATA in expressions:
        if type(DATA) is int:
            return_package += num_packer.pack(DATA)
        else:
            return_package += DATA
    return return_package


def report_data(s, expressions, num_expressions_len=2):
    string_buffer = s.recv(2048)
    read_bytes = 0
    numpacker = struct.Struct("H")
    number_of_expressions = numpacker.unpack(string_buffer[0:num_expressions_len])[0]
    read_bytes += 2
    for i in range(0, number_of_expressions):
        #  if we try to read another expression byte count w/o sufficient bytes
        while num_expressions_len > len(string_buffer) - read_bytes:
            string_buffer += s.recv(2048)
        expression_byte_count = numpacker.unpack(string_buffer[read_bytes: read_bytes + num_expressions_len])[
            0]
        read_bytes += 2
        #  get all bytes of expression to evaluate
        while expression_byte_count > len(string_buffer) - read_bytes:
            string_buffer += s.recv(2048)
        print "The Answer to Expression {0} = {1}".format(expressions[2 + 2 * i],
                                                          string_buffer[
                                                          read_bytes: read_bytes + expression_byte_count])
        read_bytes += expression_byte_count


def main(mutable_bytes):
    data_to_transmit = package_data(mutable_bytes)
    server_name = socket.gethostname()
    print 'Hostname: ', server_name
    server_port = 8181
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_name, server_port))
    print 'Connected to server ', server_name
    s.sendall(data_to_transmit)
    report_data(s, mutable_bytes)
    s.close()


main([3, 3, "1+2", 7, "1/1/1/1", 1, "7"])
