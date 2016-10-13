# This example is using Python 2.7
import socket
import struct

MAX_BUFFER_SIZE = 16


# Encode a short int to byte code using network endianess.
#
# x: int
# return: string (of length 2)
def encode_int16(x):
    return struct.pack('!h', x)


# Helper function to encode a single expression. It will return a byte
# stream with 2-byte length attached in front of "expression".
def encode_expression(expression):
    return ''.join([encode_int16(len(expression)), expression])


# Form request given a list of expressions.
def construct_message(expressions):
    return ''.join(
        [encode_int16(len(expressions))] + map(encode_expression, expressions))


# Read 'n' bytes from socket 's'.
#
# s: TCP socket object
# n: number of bytes to read
# return: a string of _exact_ n bytes
def read_n_bytes(s, n):
    parts = []
    read_bytes = 0
    while read_bytes < n:
        remain_bytes = n - read_bytes
        m = s.recv(min(MAX_BUFFER_SIZE, remain_bytes))
        parts.append(m)
        read_bytes += len(m)
    return ''.join(parts)


# Decode a short int from its byte encoding.
#
# x: byte encoding of int (of length 2)
# return: int
def decode_int16(x):
    return struct.unpack('!h', x)[0]


# Read message and parse.
#
# s: TCP socket object
# return: list_of_expressions
def read_message(s):
    num = decode_int16(read_n_bytes(s, 2))
    expressions = []
    for i in range(num):
        length = decode_int16(read_n_bytes(s, 2))
        expressions.append(read_n_bytes(s, length))
    return expressions
