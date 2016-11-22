# This example is using Python 2.7
import os.path
import socket
import threading

import table
import util

_CONFIG_UPDATE_INTERVAL_SEC = 5

_MAX_UPDATE_MSG_SIZE = 1024
_BASE_ID = 8000
_MAX_SHORT = 6534


def _ToPort(router_id):
    return _BASE_ID + router_id


def _ToRouterId(port):
    return port - _BASE_ID


def get_cost_of_route(target_router, snapshot):
    # print "Getting " + str(target_router) + " from " + str(snapshot)
    hasroute = filter(lambda x: x[0] == target_router, snapshot)
    if not len(hasroute):
        return _MAX_SHORT
    return hasroute[0][-1]


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
        self._router_id = None
        # Socket used to send/recv update messages (using UDP).
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.route_lock = threading.Lock()
        self.thread_list = []
        self.neighbor_dv = {}
        self.broadcast_msg = ""
        self.neighbor_link_costs = []

    def start(self):
        # Start a periodic closure to update config.
        # TODO: init and start other threads.
        self.read_config()
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
        self.read_config()
        print self._forwarding_table.__str__()
        for router in self.neighbor_dv.keys():
            self._socket.sendto(self.broadcast_msg, ('localhost', _ToPort(router)))

    def read_config(self):
        assert os.path.isfile(self._config_filename)
        with open(self._config_filename, 'r') as f:
            router_id = int(f.readline().strip())
            #  Make tuples for each neighbor
            neighbors = [(item[0], item[0], item[1]) for item in
                         [[int(j) for j in line.strip().split(",")] for line in f]]
            self.neighbor_link_costs = neighbors
            neighbors.append((router_id, router_id, 0))
            if not self._router_id:
                # set up socket, router id, and self.neighbor_link_cost distance vector
                self._socket.bind(('localhost', _ToPort(router_id)))
                self._router_id = router_id
                neighbor_routers = map(lambda x: x[0], neighbors)
                neighbor_routers.remove(self._router_id)
                for router in neighbor_routers:
                    self.neighbor_dv[router] = [(router, router, 0)]
                # add route to this router

                # Computes the initial snapshot
                self.route_lock.acquire()
                self._forwarding_table.reset(neighbors)
                self.route_lock.release()

            self.broadcast_msg = util.encode_message(neighbors)

    def receiver_msg(self, data):
        return util.read_message(data)

    def update_route_table(self, update_list, msg_router):
        # Discover new routers while keeping routers that I know about
        #  update list [(target router, cost)]
        link_costs = self.neighbor_link_costs
        self.neighbor_dv[msg_router] = update_list
        dv_changes = []
        print "Router " + str(self._router_id) + " received  message from  router " + str(msg_router) + " " + str(
            update_list)
        for target_router in map(lambda x: x[0], update_list):
            cost_list = []
            if target_router != self._router_id:
                for neighbor in self.neighbor_dv.keys():
                    cost_list.append((get_cost_of_route(target_router, self.neighbor_dv[neighbor]) +
                                      get_cost_of_route(neighbor, link_costs), neighbor))

                # print "Cost list: " + str(cost_list)
                new_dv, next_hop = min(cost_list)
                dv_changes.append((target_router, next_hop, new_dv))
        print "Changes to make " + str(dv_changes)
        for entry in dv_changes:
            link_costs = filter(lambda x: x[0] != entry[0], link_costs)
            link_costs.append(entry)

        link_costs.append((self._router_id, self._router_id, 0))
        self.route_lock.acquire()
        self.broadcast_msg = util.encode_message(link_costs)
        self._forwarding_table.reset(link_costs)
        self.route_lock.release()
