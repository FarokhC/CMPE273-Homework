import hashlib
import numpy

from server_config import NODES

class NodeRing():

    def __init__(self, nodes):
        assert len(nodes) > 0
        self.nodes = nodes

    def get_node(self, key_hex):
        key = int(key_hex, 16)
        node_index = key % len(self.nodes)
        return self.nodes[node_index]


def test():
    ring = NodeRing(nodes=NODES)
    node = ring.get_node('9ad5794ec94345c4873c4e591788743a')
    print(node)
    print(ring.get_node('ed9440c442632621b608521b3f2650b8'))

class NodeRingRendezvous():

    def __init__(self, nodes):
        assert len(nodes) > 0
        self.nodes = nodes

    def get_node(self, key_hex):
        weights = [0]*len(self.nodes)
        key = str(int(key_hex, 16))
        for i in range(0, len(self.nodes)):
            weights[i] = hashlib.md5((str(int(key) + i)).encode()).hexdigest()
        node_index = weights.index(max(weights))
        print("Node Index: " + str(node_index))
        return self.nodes[node_index]


def test():
    ring = NodeRing(nodes=NODES)
    node = ring.get_node('9ad5794ec94345c4873c4e591788743a')
    print(node)
    print(ring.get_node('ed9440c442632621b608521b3f2650b8'))

class NodeRingConsistentHashing():
    def __init__(self, nodes):
        assert len(nodes) > 0
        self.nodes = nodes

    def get_node(self, key_hex):
        m = (2**32) - 1

        node_index = [None]*len(self.nodes)
        for i in range(len(self.nodes)):
            node_index[i] = hash(self.nodes[i]['port']) % m
        key_index = hash(key_hex)

        #calculate closest node
        deltas = [None]*len(node_index)
        for i in range(len(node_index)):
            deltas[i] = abs(key_index - node_index[i])
        node_index = deltas.index(min(deltas))
        print("Index: " + str(node_index))

        #virtual node layer and data replication
        physical_nodes = [
            [0, 2],
            [1, 3]
        ]
        ret_nodes = None
        #use physical nodes 0 and 2
        if(node_index <= 1):
            ret_nodes = physical_nodes[0]
        #use physical onodes 1 and 3
        else:
            ret_nodes = physical_nodes[1]

        return self.nodes[ret_nodes[0]], self.nodes[ret_nodes[1]]

def test():
    ring = NodeRing(nodes=NODES)
    node = ring.get_node('9ad5794ec94345c4873c4e591788743a')
    print(node)
    print(ring.get_node('ed9440c442632621b608521b3f2650b8'))



# Uncomment to run the above local test via: python3 node_ring.py
# test()
