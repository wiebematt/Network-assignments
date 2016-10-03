# This example is using Python 2.7
import socket
import thread
import struct
from Parser import Parser

# Get host name, IP address, and port number.
# import sys

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
EXPRESSION_BYTE_COUNT_LENGTH = 2


# Handle first read


def handler(connect):
    string_buffer = connect.recv(bufsize)
    read_bytes = 0
    numpacker = struct.Struct("H")
    number_of_expressions = numpacker.unpack(string_buffer[0:EXPRESSION_BYTE_COUNT_LENGTH])[0]
    read_bytes += 2
    expressions = []
    for i in range(0, number_of_expressions):
        #  if we try to read another expression byte count w/o sufficient bytes
        while EXPRESSION_BYTE_COUNT_LENGTH > len(string_buffer) - read_bytes:
            string_buffer += connect.recv(bufsize)
        expression_byte_count = numpacker.unpack(string_buffer[read_bytes: read_bytes + EXPRESSION_BYTE_COUNT_LENGTH])[
            0]
        read_bytes += 2
        #  get all bytes of expression to evaluate
        while expression_byte_count > len(string_buffer) - read_bytes:
            string_buffer += connect.recv(bufsize)
        expressions.append(string_buffer[read_bytes: read_bytes + expression_byte_count])
        read_bytes += expression_byte_count
    # print expressions
    connect.sendall(math_handler(expressions))


def math_handler(expression_list):
    numpacker = struct.Struct("H")
    return_message = numpacker.pack(len(expression_list))
    for expression in expression_list:
        value = Parser(expression).get_value()
        return_message += numpacker.pack(len(value)) + value
    return return_message


while True:
    conn, addr = s.accept()
    print 'Server connected by', addr
    thread.start_new(handler, (conn,))
