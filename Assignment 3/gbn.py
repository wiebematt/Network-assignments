import util
import udt
import config
from threading import Timer


# Go-Back-N reliable transport protocol.

class GoBackN:
    # "msg_handler" is used to deliver messages to application layer
    # when it's ready.
    def __init__(self, local_port, remote_port, msg_handler):
        self.network_layer = udt.NetworkLayer(local_port, remote_port, self)
        self.msg_handler = msg_handler
        self.base = 1
        self.nextseqnum = 1
        self.timer = None
        self.inflight = {}
        self.ackpkt = util.encode_pkt(0, "", config.MSG_TYPE_ACK)
        self.lock = False
        self.sender = local_port == config.SENDER_LISTEN_PORT

    def timer_start(self):
        self.timer = Timer(config.TIMEOUT_MSEC / 1000.0, self.timeout)
        self.timer.start()

    # "send" is called by application. Return true on success, false
    # otherwise.
    def send(self, msg):
        if len(msg) <= config.MAX_MESSAGE_SIZE or self.nextseqnum < self.base + config.WINDOWN_SIZE:
            pkt = util.encode_pkt(self.nextseqnum, msg, config.MSG_TYPE_DATA)
            while self.lock:
                pass
            self.lock = True
            self.inflight[self.nextseqnum] = pkt
            self.lock = False
            if self.base == self.nextseqnum:
                self.timer_start()
            self.nextseqnum = (self.nextseqnum + 1) % config.WINDOWN_SIZE
            self.network_layer.send(pkt)
            return True
        else:
            return False

    # "handler" to be called by network layer when packet is ready.
    def handle_arrival_msg(self):
        msg = self.network_layer.recv()
        msg_type, seqnum, chksum, corrupt_chk, msg = util.decode_pkt(msg)
        if corrupt_chk:
            if msg_type == config.MSG_TYPE_DATA:
                # receiver

                if seqnum == self.nextseqnum:
                    self.msg_handler(msg)
                    self.ackpkt = util.encode_pkt(self.nextseqnum, "", config.MSG_TYPE_ACK)
                    self.network_layer.send(self.ackpkt)
                    self.nextseqnum = (self.nextseqnum + 1) % config.WINDOWN_SIZE
                else:
                    self.network_layer.send(self.ackpkt)
            elif msg_type == config.MSG_TYPE_ACK:
                # sender
                self.base = (seqnum + 1) % config.WINDOWN_SIZE
                while self.lock:
                    pass
                self.lock = True
                for key in self.inflight:
                    pass
                self.lock = False
            else:
                if not self.sender:
                    self.network_layer.send(self.ackpkt)
                    # if msg_type == config.MSG_TYPE_DATA:
                    #     # receiver
                    #     if seqnum == self.nextseqnum:
                    #         self.msg_handler(msg)
                    #         ackpkt = util.encode_pkt(seqnum, "", config.MSG_TYPE_ACK)
                    #
                    #         self.network_layer.send(ackpkt)
                    #         self.nextseqnum = (self.nextseqnum + 1) % config.WINDOWN_SIZE
                    # #
                    # elif msg_type == config.MSG_TYPE_ACK:
                    #     # sender
                    #     # print "Seqnum #" + str(seqnum) + " base: " + str(self.base)
                    #     self.base = (seqnum + 1) % config.WINDOWN_SIZE
                    #     while self.lock:
                    #         pass
                    #     self.lock = True
                    #     # cumulative acknowledgement
                    #     print self.inflight.keys()
                    #     cum_ack = (seqnum + config.WINDOWN_SIZE -1) % config.WINDOWN_SIZE
                    #     for key in self.inflight.keys():
                    #         if int(key) <= seqnum:
                    #             self.inflight.pop(key)
                    #             print "removed " + str(key)
                    #     self.lock = False
                    #
                    #     if self.base == self.nextseqnum:
                    #         self.timer.cancel()
                    #     else:
                    #         self.timer_start()

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
        for i in range(len(self.inflight)):
            self.timeout()
        self.network_layer.shutdown()
