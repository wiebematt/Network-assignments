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
        self.timer = None
        self.inflight = ""
        self.sender = local_port == config.SENDER_LISTEN_PORT

    # "send" is called by application. Return true on success, false
    # otherwise.
    def send(self, msg):
        if len(msg) > config.MAX_MESSAGE_SIZE or self.waitforack:
            return False
        else:
            self.inflight = util.encode_pkt(self.nextseqnum, msg, config.MSG_TYPE_DATA)
            self.waitforack = True
            self.timer_start()
            # print "sent " + msg
            self.network_layer.send(self.inflight)
            return True

    def timer_start(self):
        self.timer = Timer(config.TIMEOUT_MSEC / 1000.0, self.timeout)
        self.timer.start()

    def timeout(self):
        # print "TIMEOUT: " + str([util.decode_pkt(self.inflight)])
        self.waitforack = True
        self.timer_start()
        self.network_layer.send(self.inflight)

    def handle_arrival_msg(self):
        msg = self.network_layer.recv()
        msg_type, seqnum, chksum, not_corrupt, msg = util.decode_pkt(msg)
        # print [seqnum, self.nextseqnum, not_corrupt, msg]
        if not_corrupt and seqnum == self.nextseqnum:
            if msg_type == config.MSG_TYPE_DATA and not self.sender:
                # print "received data " + msg
                self.msg_handler(msg)
                self.inflight = util.encode_pkt(self.nextseqnum, "", config.MSG_TYPE_ACK)
                self.nextseqnum = (self.nextseqnum + 1) % 2
                self.network_layer.send(self.inflight)
            elif self.waitforack and msg_type == config.MSG_TYPE_ACK and self.sender:
                # print "received ack: " + str(seqnum) + " " + str(msg_type)
                self.timer.cancel()
                self.nextseqnum = (self.nextseqnum + 1) % 2
                self.waitforack = False
            else:
                print "Fail " + str([msg_type, seqnum, chksum, not_corrupt, msg]) + " isSender: " + str(self.sender)
        elif not self.sender:
            self.network_layer.send(self.inflight)
        else:
            pass
            # print "Received Ack: " + str(seqnum) + " vs. sent msg num " + str(self.nextseqnum)

    def shutdown(self):
        while self.waitforack:
            pass
        self.network_layer.shutdown()
