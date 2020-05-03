import sys
import socket
import functools

from sample_data import USERS
from server_config import NODES
from pickle_hash import serialize_GET, serialize_PUT, serialize_DELETE
import node_ring
from bloom_filter import BloomFilter

BUFFER_SIZE = 1024
bloomFilter = BloomFilter()
cache = []

def add_to_lru_cache(data):
    try:
        cache.append(cache.pop(0))
    except:
        print("cache empty")
    cache.append(data)

def get_lru_cache(data):
    try:
        for i in range (0, len(cache)):
            if(cache[i][0]['key'] == data.decode("utf-8")):
                return cache[i]
    except Exception as e:
        print(str(e))
        return False
    return False

def delete_lru_cache(data):
    try:
        for i in range (0, len(cache)):
            if(cache[i][0]['key'] == data.decode("utf-8")):
                cache[i].pop(i)

        return True
    except Exception as e:
        print(str(e))
        return False
    return False

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
        put(hash_codes, u)

    print(f"Number of Users={len(USERS)}\nNumber of Users Cached={len(hash_codes)}")

    for hc in hash_codes:
        get(hc)

    for hc in hash_codes:
        delete(hc)

    print(f"Number of Users={len(USERS)}\nNumber of Users Cached={len(hash_codes)}")

    print("Done!")

def lru_cache(*args, **kwargs):
    def wrapper(func):
        def f(*args):
            func_name = func.__name__
            hash_codes = args[0]
            if(func_name == 'put'):
                user = args[1]
                data_bytes, key = serialize_PUT(user)
                data = [{'key': key}, {'data_bytes': data_bytes}]
                add_to_lru_cache(data)
                return func(hash_codes, user, key, data_bytes)
            elif(func_name == 'get'):
                for i in range(0, len(cache)):
                    data_bytes, key = serialize_GET(hash_codes)
                    data = get_lru_cache(key)
                    if(data == False):
                        return func(hash_codes, data_bytes, key)
                    else:
                        print("Local LRU Cache Response: " + str(data) + "\n")
            elif(func_name == 'delete'):
                for i in range(0, len(cache)):
                    data_bytes, key = serialize_GET(hash_codes)
                    data = delete_lru_cache(key)
                    if(data == False):
                        print("{} not in cache for delete operation".format(str(key)))
                    else:
                        print("Deleted {} from cache".format(str(key)))
                    return func(hash_codes, data_bytes, key)
            print("hashcodes: " + str(hash_codes))

        return f
    return wrapper

@lru_cache(5)
def put(hash_codes, user, key, data_bytes):
    # PUT all users.
    bloomFilter.add(key)
    # TODO: PART II - Instead of going to server 0, use Naive hashing to split data into multiple servers
    nr = node_ring.NodeRing(NODES)
    node = nr.get_node(key)
    client = UDPClient(node['host'], node['port'])
    response = client.send(data_bytes)
    hash_codes.add(response)
    print(response)

@lru_cache(5)
def get(hash_code, data_bytes, key):
    # TODO: PART I
    # GET all users.
    print(hash_code)
    nr = node_ring.NodeRing(NODES)
    node = nr.get_node(key)
    if(bloomFilter.is_member(key)):
        print("in cache")
        client = UDPClient(node['host'], node['port'])
        response = client.send(data_bytes)
    else:
        response = "Key {} not found in Bloom Filter for get request".format(key)
    print(str(response))

@lru_cache(5)
def delete(hash_code, data_bytes, key):
    # Delete all users
    print(hash_code)
    data_bytes, key = serialize_DELETE(hash_code)
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
