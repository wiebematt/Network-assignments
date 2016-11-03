import udt
import config
import util
from threading import Timer


# Stop-And-Wait reliable transport protocol.
class StopAndWait:
    # "msg_handler" is used to deliver messages to application layer
    # when it's ready.
    def __init__(self, local_port, remote_port, msg_handler):
        self.network_layer = udt.NetworkLayer(local_port, remote_port, self)
        self.msg_handler = msg_handler
        self.nextseqnum = 0
        self.waitforack = False
        self.timer = Timer(config.TIMEOUT_MSEC / 1000, self.timeout)
        self.inflight = ""

    # "send" is called by application. Return true on success, false
    # otherwise.
    def send(self, msg):
        if len(msg) > config.MAX_MESSAGE_SIZE or self.waitforack:
            return False
        else:
            self.inflight = util.encode_pkt(self.nextseqnum, msg, config.MSG_TYPE_DATA)
            self.waitforack = True
            self.timer.start()
            print "sent"
            self.network_layer.send(self.inflight)

    def timeout(self):
        print "TIMEOUT"
        self.timer = Timer(config.TIMEOUT_MSEC / 1000, self.timeout)
        self.waitforack = True
        self.timer.start()
        self.network_layer.send(self.inflight)

    def handle_arrival_msg(self):
        msg = self.network_layer.recv()
        msg_type, seqnum, chksum, corrupt_chk, msg = util.decode_pkt(msg)
        if corrupt_chk and seqnum == self.nextseqnum:
            if msg_type == config.MSG_TYPE_DATA:
                print "received data"
                self.msg_handler(msg)
                self.nextseqnum += (self.nextseqnum + 1) % 2
                ackpkt = util.encode_pkt(self.nextseqnum, "", config.MSG_TYPE_ACK)
                self.network_layer.send(ackpkt)
            elif self.waitforack and msg_type == config.MSG_TYPE_ACK:
                print "received ack"
                if (self.nextseqnum + 1) % 2 == seqnum:
                    self.timer.cancel()
                    self.nextseqnum = (self.nextseqnum + 1) % 2
                    self.waitforack = False
        else:
            ackpkt = util.encode_pkt(self.nextseqnum, "", config.MSG_TYPE_ACK)
            self.network_layer.send(ackpkt)


# Cleanup resources.
def shutdown(self):
    self.network_layer.shutdown()
    self.timer.cancel()
