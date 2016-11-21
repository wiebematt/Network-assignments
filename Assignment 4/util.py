# This example is using Python 2.7
import threading
import struct


# Convenient class to run a function periodically in a separate
# thread.
class PeriodicClosure:
    def __init__(self, handler, interval_sec):
        self._handler = handler
        self._interval_sec = interval_sec
        self._timer = None

    def _timeout_handler(self):
        self._handler()
        self.start()

    def start(self):
        self._timer = threading.Timer(self._interval_sec, self._timeout_handler)
        self._timer.start()

    def stop(self):
        if self._timer:
            self._timer.cancel()


# Encode a short int to byte code using network endianess.
# x: int
# return: string (of length 2)
def encode_int16(x):
    return struct.pack('!h', x)


# Decode a short int from its byte encoding.
#
# x: byte encoding of int (of length 2)
# return: int
def decode_int16(x):
    return struct.unpack('!h', x)[0]


# Read message and parse.
# return: list_of_expressions
def read_message(data):
    num = decode_int16(data[:2])
    data = data[2:]
    if len(data) >= 2 * num:
        expressions = []
        for i in range(num):
            destination = decode_int16(data[:2])
            data = data[2:]
            cost = decode_int16(data[:2])
            data = data[2:]
            expressions.append((destination, cost))
        return expressions


# def append_router_id(router_id, neighbors):
#     l = [(router_id, pair[0], pair[1]) for pair in neighbors]
#     l.append((router_id, router_id, 0))
#     return l


def filter_on_host(router_list, router):
    return filter(lambda x: x[0] == router, router_list)


def encode_message(router_list):
    msg = encode_int16(len(router_list))
    for target_router, next_hop, cost in router_list:
        msg += encode_int16(target_router) + encode_int16(cost)
    return msg
