import dummy
import gbn
import ss
import struct


def get_transport_layer_by_name(name, local_port, remote_port, msg_handler):
    assert name == 'dummy' or name == 'ss' or name == 'gbn'
    if name == 'dummy':
        return dummy.DummyTransportLayer(local_port, remote_port, msg_handler)
    if name == 'ss':
        return ss.StopAndWait(local_port, remote_port, msg_handler)
    if name == 'gbn':
        return gbn.GoBackN(local_port, remote_port, msg_handler)


def encode_pkt(seqnum, msg, msg_type):
    return encode_int16(msg_type) + encode_int16(seqnum) + encode_int16(
        compute_chksum(seqnum, msg_type, msg)) + msg


def decode_pkt(msg):
    # print str([msg[:6][i:i + 2] for i in range(0, 6, 2)])
    msg_type, seqnum, chksum = map(decode_int16, [msg[:6][i:i + 2] for i in range(0, 6, 2)])
    body = msg[6:]
    corrupt_chk = chksum == compute_chksum(seqnum, msg_type, body)
    return msg_type, seqnum, chksum, corrupt_chk, body


def compute_chksum(seqnum, msg_type, msg):
    s = seqnum + msg_type
    if len(msg) % 2 != 0:
        msg += "\x00"
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i + 1]) << 8)
        s = carry_around_add(s, w)
    # val = ~s & 0xffff
    # print "Seqnum: " + str(seqnum) + " Val: " + str(val) + " " + msg
    return ~s & 0xffff


def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)


def encode_int16(x):
    return struct.pack('!H', x)


def decode_int16(x):
    return struct.unpack('!H', x)[0]
