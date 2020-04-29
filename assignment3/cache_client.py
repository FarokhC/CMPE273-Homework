import sys
import socket

from sample_data import USERS
from server_config import NODES
from pickle_hash import serialize_GET, serialize_PUT, serialize_DELETE
import node_ring
from bloom_filter import BloomFilter

BUFFER_SIZE = 1024
bloomFilter = BloomFilter()

class UDPClient():
    def __init__(self, host, port):
        self.host = host
        self.port = int(port)

    def send(self, request):
        print('Connecting to server at {}:{}'.format(self.host, self.port))
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(request, (self.host, self.port))
            response, ip = s.recvfrom(BUFFER_SIZE)
            return response
        except socket.error:
            print("Error! {}".format(socket.error))
            exit()

    cache = {}

def process(udp_clients):
    hash_codes = set()

    put(hash_codes)

    print(f"Number of Users={len(USERS)}\nNumber of Users Cached={len(hash_codes)}")

    get(hash_codes)

    delete(hash_codes)

    print(f"Number of Users={len(USERS)}\nNumber of Users Cached={len(hash_codes)}")

    print("Done!")

# def lru_cache(func, *args, **kwargs):
#     print("In decorator. cache_size: {}".format(args[0]))
#     print(args)
#     print(kwargs)
#     func()
#     return "hi"

# @lru_cache(5)
def put(hash_codes):
    # PUT all users.
    for u in USERS:
        data_bytes, key = serialize_PUT(u)
        bloomFilter.add(key)
        # TODO: PART II - Instead of going to server 0, use Naive hashing to split data into multiple servers
        nr = node_ring.NodeRing(NODES)
        node = nr.get_node(key)
        client = UDPClient(node['host'], node['port'])
        response = client.send(data_bytes)
        hash_codes.add(response)
        print(response)

def get(hash_codes):
    # TODO: PART I
    # GET all users.
    for hc in hash_codes:
        print(hc)
        data_bytes, key = serialize_GET(hc)
        print('get key: ' + str(key))
        nr = node_ring.NodeRing(NODES)
        node = nr.get_node(key)

        if(bloomFilter.is_member(key)):
            print("in cache")
            client = UDPClient(node['host'], node['port'])
            response = client.send(data_bytes)
        else:
            response = "Key {} not found in Bloom Filter for get request".format(key)
        print(str(response))


def delete(hash_codes):
    # Delete all users
    for hc in hash_codes:
        print(hc)
        data_bytes, key = serialize_DELETE(hc)
        print('delete key: ' + str(key))
        nr = node_ring.NodeRing(NODES)
        node = nr.get_node(key)

        if(bloomFilter.is_member(key)):
            client = UDPClient(node['host'], node['port'])
            response = client.send(data_bytes)
        else:
            response = "Key {} not found in Bloom Filter for delete request".format(key)
        print(str(response))

if __name__ == "__main__":
    clients = [
        UDPClient(server['host'], server['port'])
        for server in NODES
    ]
    process(clients)
