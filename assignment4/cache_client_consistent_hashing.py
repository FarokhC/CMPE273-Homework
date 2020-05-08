import sys
import socket
import functools

from sample_data import USERS
from server_config import NODES
from pickle_hash import serialize_GET, serialize_PUT, serialize_DELETE
import node_ring
from bloom_filter import BloomFilter
from lru_cache import lru_cache
import hashlib

BUFFER_SIZE = 1024
NUM_KEYS = 20
FALSE_POSITIVE_PROBABILITY = 0.05
bloomFilter = BloomFilter(NUM_KEYS, FALSE_POSITIVE_PROBABILITY)

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

    for u in USERS:
        data_bytes, key = serialize_PUT(u)
        put(hash_codes, data_bytes, key)

    print(f"Number of Users={len(USERS)}\nNumber of Users Cached={len(hash_codes)}")

    for hc in hash_codes:
        data_bytes, key = serialize_GET(u)
        print('ley: ' + str(key))
        hash_code = hashlib.md5(str(key).encode())
        hash_val = hash_code.hexdigest()
        print("hash val: " + str(hash_val))
        get(hash_val, data_bytes, hash_codes)

    for hc in hash_codes:
        data_bytes, key = serialize_DELETE(u)
        delete(hc, data_bytes, key)

    print(f"Number of Users={len(USERS)}\nNumber of Users Cached={len(hash_codes)}")

    print("Done!")


def put(hash_code, data_bytes, key):
    # PUT all users.
    bloomFilter.add(key)
    # TODO: PART II - Instead of going to server 0, use Naive hashing to split data into multiple servers
    nr = node_ring.NodeRingConsistentHashing(NODES)
    print("put key: " + str(key))
    node = nr.get_node(key)
    for n in node:
        client = UDPClient(n['host'], n['port'])
        response = client.send(data_bytes)
    hash_code.add(response)
    print(response)

@lru_cache(5)
def get(key, data_bytes, hashcode):
    # TODO: PART I
    # GET all users.
    print("ke: " + str(key))

    nr = node_ring.NodeRingConsistentHashing(NODES)
    print('key: ' + str(key))
    node = nr.get_node(key)
    if(bloomFilter.is_member(key)):
        print("in cache")
        for n in node:
            client = UDPClient(n['host'], n['port'])
            response = client.send(data_bytes)
    else:
        response = "Key {} not found in Bloom Filter for get request".format(key)
    print(str(response))

def delete(hash_code, data_bytes, key):
    # Delete all users
    print(hash_code)
    data_bytes, key = serialize_DELETE(hash_code)
    print('delete key: ' + str(key))
    nr = node_ring.NodeRingConsistentHashing(NODES)
    node = nr.get_node(key)
    if(bloomFilter.is_member(key)):
        for n in node:
            client = UDPClient(n['host'], n['port'])
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
