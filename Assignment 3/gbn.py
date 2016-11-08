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
        self.base = 0
        self.nextseqnum = 0
        self.timer = None
        self.inflight = []
        self.ackpkt = util.encode_pkt(0, "", config.MSG_TYPE_ACK)
        self.lock = False
        self.sender = local_port == config.SENDER_LISTEN_PORT
        self.shutdown_flag = False

    def timer_start(self):
        self.timer = Timer(config.TIMEOUT_MSEC / 1000.0, self.timeout)
        self.timer.start()

    # "send" is called by application. Return true on success, false
    # otherwise.
    def send(self, msg):
        if len(msg) <= config.MAX_MESSAGE_SIZE and self.nextseqnum < self.base + config.WINDOWN_SIZE:
            pkt = util.encode_pkt(self.nextseqnum, msg, config.MSG_TYPE_DATA)
            while self.lock:
                pass
            self.lock = True
            if len(self.inflight) == config.WINDOWN_SIZE:
                self.inflight[self.nextseqnum % config.WINDOWN_SIZE] = pkt
            else:
                self.inflight.append(pkt)
            self.lock = False
            if self.base == self.nextseqnum:
                self.timer_start()
            self.nextseqnum += 1
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
                    print "Sent ack " + str(self.nextseqnum)
                    self.network_layer.send(self.ackpkt)
                    self.nextseqnum += 1
                else:
                    self.network_layer.send(self.ackpkt)
            elif msg_type == config.MSG_TYPE_ACK:
                # sender

                self.base = seqnum + 1
                if self.base == self.nextseqnum:
                    self.timer.cancel()
                else:
                    self.timer.cancel()
                    self.timer_start()
            else:
                if not self.sender:
                    self.network_layer.send(self.ackpkt)

    def timeout(self):
        while self.lock:
            pass
        self.lock = True
        print "Base: " + str(self.base) + " Nextseqnum: " + str(self.nextseqnum)
        current = self.base
        while True:
            # print current
            self.network_layer.send(self.inflight[current % config.WINDOWN_SIZE])
            current += 1
            if current == self.nextseqnum:
                break
        self.lock = False

    # Cleanup resources.
    def shutdown(self):
        self.shutdown_flag = True
        while self.base != self.nextseqnum:
            pass
        self.network_layer.shutdown()
