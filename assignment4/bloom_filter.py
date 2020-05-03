import hashlib
import pickle
import sys

bloom_filter_size = 999999999

class BloomFilter():
    def __init__(self):
        self.arr = [0] * bloom_filter_size
        self.k = 100

    def add(self, key):
        count = 0
        updated_key = key
        updated_key = int(updated_key, 16)

        while count < self.k:
            count += 1
            index = hash(updated_key)
            index = self.process_index(index)

            self.arr[index] = 1
            updated_key = int(updated_key) / 9

    def is_member(self, key):
        count = 1
        updated_key = key
        updated_key = int(updated_key, 16)
        index = hash(updated_key)
        index = self.process_index(index)
        updated_key = int(updated_key) / 9

        while count < self.k:
            if(int(self.arr[index]) >= 1):
                count += 1
            if str(self.arr[index]) == 0:
                break
            index = hash(updated_key)
            index = self.process_index(index)
            updated_key = int(updated_key) / 9
        if count == self.k:
            return True
        else:
            return False

    def process_index(self, index):
        if(index < 0):
            index += sys.maxsize
        if(index >= bloom_filter_size):
            index = index % bloom_filter_size
        return index
