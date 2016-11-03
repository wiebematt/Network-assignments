import util
import udt
import config
from threading import Timer, RLock


# Go-Back-N reliable transport protocol.

class GoBackN:
    # "msg_handler" is used to deliver messages to application layer
    # when it's ready.
    def __init__(self, local_port, remote_port, msg_handler):
        self.network_layer = udt.NetworkLayer(local_port, remote_port, self)
        self.msg_handler = msg_handler
        self.base = 1
        self.nextseqnum = 1
        self.expectedseqnum = 1
        self.timer = Timer(config.TIMEOUT_MSEC / 1000, self.timeout)
        self.inflight = {}
        self.lock = RLock()

    # "send" is called by application. Return true on success, false
    # otherwise.
    def send(self, msg):
        if len(msg) > config.MAX_MESSAGE_SIZE or self.nextseqnum >= self.base + config.WINDOWN_SIZE:
            return False
        else:

            pkt = util.encode_pkt(self.nextseqnum, msg, config.MSG_TYPE_DATA)
            if self.base == self.nextseqnum:
                self.timer = Timer(config.TIMEOUT_MSEC / 1000, self.timeout)
                self.timer.start()
            with self.lock:
                self.inflight[self.nextseqnum] = pkt
            self.nextseqnum += 1
            print "Packet sent: " + str(self.nextseqnum)
            self.network_layer.send(pkt)
            return True

    # "handler" to be called by network layer when packet is ready.
    def handle_arrival_msg(self):
        msg = self.network_layer.recv()
        msg_type, seqnum, chksum, corrupt_chk, msg = util.decode_pkt(msg)
        if corrupt_chk:
            if msg_type == config.MSG_TYPE_DATA and seqnum == self.expectedseqnum:
                self.msg_handler(msg)
                ackpkt = util.encode_pkt(seqnum, "", config.MSG_TYPE_ACK)
                self.expectedseqnum += 1
                self.network_layer.send(ackpkt)
            elif msg_type == config.MSG_TYPE_ACK:
                print "ack received"
                base = seqnum + 1
                self.timer.cancel()
                print "All ACK'ed"
                if base != self.nextseqnum:
                    print "Timer restart"
                    self.timer = Timer(config.TIMEOUT_MSEC / 1000, self.timeout)
                    self.timer.start()
                with self.lock:
                    self.inflight.pop(seqnum, "ACK already received")

    def timeout(self):
        # self.timer = threading.Timer(config.TIMEOUT_MSEC / 1000, self.timeout)
        # self.timer.start()
        with self.lock:
            for key in self.inflight:
                self.network_layer.send(self.inflight[key])

    # Cleanup resources.
    def shutdown(self):
        self.timer.cancel()
        self.network_layer.shutdown()
