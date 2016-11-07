import util
import udt
import config
from threading import Timer
import time


# Go-Back-N reliable transport protocol.

class GoBackN:
    # "msg_handler" is used to deliver messages to application layer
    # when it's ready.
    def __init__(self, local_port, remote_port, msg_handler):
        self.waitforack = False
        self.network_layer = udt.NetworkLayer(local_port, remote_port, self)
        self.msg_handler = msg_handler
        self.base = 0
        self.MAX_SEQNUM = 40
        self.nextseqnum = 0
        self.expectedseqnum = 0
        self.timer = Timer(config.TIMEOUT_MSEC / 1000.0, self.timeout)
        self.inflight = {}
        self.lock = False
        self.sender = local_port == config.SENDER_LISTEN_PORT

    def timer_start(self):
        self.timer = Timer(config.TIMEOUT_MSEC / 1000.0, self.timeout)
        self.timer.start()

    # "send" is called by application. Return true on success, false
    # otherwise.
    def send(self, msg):
        if len(msg) > config.MAX_MESSAGE_SIZE or self.nextseqnum >= self.base + config.WINDOWN_SIZE:
            return False
        else:
            pkt = util.encode_pkt(self.nextseqnum, msg, config.MSG_TYPE_DATA)
            while self.lock:
                pass
            self.lock = True
            self.inflight[self.nextseqnum] = pkt
            self.lock = False
            if self.base == self.nextseqnum:
                self.timer_start()
            self.nextseqnum = (self.nextseqnum + 1) % self.MAX_SEQNUM
            self.network_layer.send(pkt)
            return True

    # "handler" to be called by network layer when packet is ready.
    def handle_arrival_msg(self):
        msg = self.network_layer.recv()
        msg_type, seqnum, chksum, corrupt_chk, msg = util.decode_pkt(msg)
        if corrupt_chk:
            if msg_type == config.MSG_TYPE_DATA:
                if seqnum == self.expectedseqnum:
                    self.msg_handler(msg)
                    ackpkt = util.encode_pkt(seqnum, "", config.MSG_TYPE_ACK)
                    print "Seqnum received: " + str(seqnum) + " expected: " + str(self.expectedseqnum)
                    self.expectedseqnum = (self.expectedseqnum + 1) % self.MAX_SEQNUM
                    self.network_layer.send(ackpkt)
                else:
                    # print "Seqnum received: " + str(seqnum) + " expected: " + str(self.expectedseqnum)
                    # not handling ack incrementation
                    self.network_layer.send(util.encode_pkt(self.expectedseqnum, "", config.MSG_TYPE_ACK))
            elif msg_type == config.MSG_TYPE_ACK:
                print "Seqnum #" + str(seqnum) + " base: " + str(self.base)
                if seqnum in self.inflight and seqnum == self.base:
                    self.base = (seqnum + 1) % self.MAX_SEQNUM
                    while self.lock:
                        pass
                    self.lock = True
                    # print "Removing: " + str(seqnum)
                    self.inflight.pop(seqnum)
                    self.lock = False

                if self.base == self.nextseqnum:
                    self.timer.cancel()
                else:
                    self.timer_start()

    def timeout(self):
        while self.lock:
            pass
        self.lock = True
        print "TIMEOUT KEYS: " + str(self.inflight.keys())
        for key in self.inflight.keys():
            self.network_layer.send(self.inflight[key])
        self.lock = False

    # Cleanup resources.
    def shutdown(self):
        print "Shutdown requested " + str(self.inflight.keys())
        # while len(self.inflight.keys()):
        #     self.timeout()
        #     time.sleep(1)
        self.timeout()
        self.network_layer.shutdown()
