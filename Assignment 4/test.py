import os

import sys

assert os.path.isfile("config/small-1")
with open("config/small-1", 'r') as f:
    router_id = int(f.readline().strip())
    neighbors = [(item[0], item[0], item[1]) for item in [[int(j) for j in line.strip().split(",")] for line in f]]
    print neighbors
    # neighbors.append((router_id, router_id, 0))
snapshot = [] + neighbors
print neighbors
