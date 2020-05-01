import hashlib

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
        virtual_nodes = 8
        m = (2**32) - 1

        node_index = [None]*virtual_nodes
        for i in range(len(node_index)):
            node_index[i] = int(hashlib.md5((str(i)).encode()).hexdigest(), 16) % m
        key_index = int(hashlib.md5(str(key_hex).encode()).hexdigest(), 16)

        #calculate closest node
        deltas = [None]*virtual_nodes
        for i in range(virtual_nodes):
            deltas[i] = abs(key_index - node_index[i])
        node_index = deltas.index(min(deltas))

        #Virtual node layer and replication
        virtual_to_physical_with_replication = [
            [0, 1],
            [2, 3],
            [4, 5],
            [6, 7]
        ]
        ret_nodes = None
        if(node_index == 0 or node_index == 1):
            ret_nodes = 0
        elif(node_index == 2 or node_index == 3):
            ret_nodes = 1
        elif(node_index == 4 or node_index == 5):
            ret_nodes = 2
        elif(node_index == 6 or node_index == 7):
            ret_nodes = 3


        first_node = ret_nodes
        second_node = (ret_nodes + 1) % 4

        print("Ret nodes: " + str(self.nodes[first_node]) +  str(self.nodes[second_node]))
        return self.nodes[first_node], self.nodes[second_node]

def test():
    ring = NodeRing(nodes=NODES)
    node = ring.get_node('9ad5794ec94345c4873c4e591788743a')
    print(node)
    print(ring.get_node('ed9440c442632621b608521b3f2650b8'))



# Uncomment to run the above local test via: python3 node_ring.py
# test()
