# This example is using Python 2.7
import os.path
import socket
import threading

import table
import util

_CONFIG_UPDATE_INTERVAL_SEC = 5

_MAX_UPDATE_MSG_SIZE = 1024
_BASE_ID = 8000
_MAX_SHORT = 65534


def _ToPort(router_id):
    return _BASE_ID + router_id


def _ToRouterId(port):
    return port - _BASE_ID


def get_cost_of_route(target_router, snapshot):
    # print "Getting " + str(target_router) + " from " + str(snapshot)
    return filter(lambda x: x[0] == target_router, snapshot)[0][-1]


def get_target_routers_from_list(router_list):
    return map(lambda x: x[0], router_list)


#
# def add_to_each_row(snapshot, known_routers, unknown_routers):
#     for knwn in known_routers:
#         for unkwn in unknown_routers:
#             snapshot.append((knwn, unkwn, _MAX_SHORT))
#     return snapshot
#
#
# def make_new_row(snapshot, known_routers, unknown_routers):
#     for unk_rout in unknown_routers:
#         for possible_router in known_routers + unknown_routers:
#             if possible_router != unk_rout:
#                 snapshot.append((unk_rout, possible_router, _MAX_SHORT))
#             else:
#                 snapshot.append((unk_rout, unk_rout, 0))
#     return snapshot


def get_removal_index(tup, router_list):
    for index, item in enumerate(router_list):
        if item[0] == tup[0]:
            return index


class Router:
    def __init__(self, config_filename):
        # ForwardingTable has 3 columns (DestinationId,NextHop,Cost). It's
        # threadsafe.
        self._config_updater = util.PeriodicClosure(
            self.load_config, _CONFIG_UPDATE_INTERVAL_SEC)
        self._forwarding_table = table.ForwardingTable()
        # Config file has router_id, neighbors, and link cost to reach
        # them.
        self._config_filename = config_filename
        self._file_time = os.stat(config_filename).st_mtime
        self._router_id = None
        # Socket used to send/recv update messages (using UDP).
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.route_lock = threading.Lock()
        self.thread_list = []
        self.known_routers = []
        self.neighbor_routers = []
        self.broadcast_msg = ""

    def start(self):
        # Start a periodic closure to update config.
        # TODO: init and start other threads.
        self._init_route_table()
        print self._forwarding_table.__str__()
        self._config_updater.start()
        while True:
            data, addr = self._socket.recvfrom(_MAX_UPDATE_MSG_SIZE)
            if len(data) > 2:
                msg = self.receiver_msg(data)
                if msg:
                    t = threading.Thread(target=self.update_route_table, args=(msg, _ToRouterId(addr[1])))
                    self.thread_list.append(t)
                    t.start()

    def stop(self):
        if self._config_updater:
            self._config_updater.stop()
            # TODO: clean up other threads.
        if threading.active_count:
            for thread in self.thread_list:
                thread.join(.5)
                if thread.isAlive():
                    thread.join(2)
        self._socket.close()

    def load_config(self):
        assert os.path.isfile(self._config_filename)
        # if self._file_time != os.stat(self._config_filename).st_mtime:
        #     self._file_time = os.stat(self._config_filename).st_mtime
        #     self._init_route_table()
        # print "File change"
        # self._init_route_table()

        print self._forwarding_table.__str__()
        for router in self.neighbor_routers:
            self._socket.sendto(self.broadcast_msg, ('localhost', _ToPort(router)))

    def _init_route_table(self):
        assert os.path.isfile(self._config_filename)
        with open(self._config_filename, 'r') as f:
            router_id = int(f.readline().strip())
            if not self._router_id:
                self._socket.bind(('localhost', _ToPort(router_id)))
                self._router_id = router_id
            # target router, next router , cost
            neighbors = [(item[0], item[0], item[1]) for item in
                         [[int(j) for j in line.strip().split(",")] for line in f]]
        self.neighbor_routers = map(lambda x: x[0], neighbors)
        self.broadcast_msg = util.encode_message(neighbors)
        neighbors.append((self._router_id, self._router_id, 0))
        self.known_routers = [self._router_id] + self.neighbor_routers
        # Computes the initial snapshot
        self.route_lock.acquire()
        self._forwarding_table.reset(neighbors)
        self.route_lock.release()

    def receiver_msg(self, data):
        return util.read_message(data)

    def update_route_table(self, update_list, msg_router):
        # Discover new routers while keeping routers that I know about
        #  update list [(target router, cost)]
        snapshot = self._forwarding_table.snapshot()
        # snapshot = self.discover_new_routers(snapshot, update_list, msg_router)

        dv_changes = []
        for router in get_target_routers_from_list(update_list):
            # if router != self._router_id:
            old_dv = get_cost_of_route(router, snapshot)
            new_dv = get_cost_of_route(msg_router, snapshot) + get_cost_of_route(router, update_list)
            if new_dv < old_dv:
                print "Change occured " + ", ".join((str(router), str(msg_router), str(new_dv)))
                dv_changes.append((router, msg_router, new_dv))
        if dv_changes:
            for entry in dv_changes:
                print "Before change : " + str(snapshot)
                # snapshot.pop(get_removal_index(entry, snapshot))
                snapshot = filter(lambda x: x[0] != entry[0], snapshot)
                print "After pop : " + str(snapshot)
                snapshot.append(entry)
                print "After append : " + str(snapshot)

            self.route_lock.acquire()
            self.broadcast_msg = util.encode_message(snapshot)
            self._forwarding_table.reset(snapshot)
            self.route_lock.release()

    def discover_new_routers(self, snapshot, update_list, next_hop):
        unknown_routers = filter(lambda x: x[0] in self.known_routers, update_list)
        for target_router, cost in unknown_routers:
            snapshot.append((target_router, next_hop, cost))
            self.known_routers.append(target_router)
        return snapshot
