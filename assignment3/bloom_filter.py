import hashlib
import pickle
import sys
import math

class BloomFilter():
    def __init__(self, keys, false_positive_rate):
        self.keys = keys
        self.false_positive_rate = false_positive_rate
        self.arr_size = int(-1 * ((keys * math.log(self.false_positive_rate)) / (math.log(2)**2)))
        self.arr = [0] * self.arr_size

    def add(self, key):
        count = 0

        while count < self.keys:
            count += 1
            index = hashlib.md5(key.encode('utf-8'))
            index = index.hexdigest()
            index = int(index, 16)
            index = self.process_index(index)
            self.arr[index] = 1

    def is_member(self, key):
        count = 1
        if(isinstance(key, str)):
            index = hashlib.md5(key.encode('utf-8'))
        else:
            index = hashlib.md5(key)
        index = index.hexdigest()
        index = int(index, 16)
        index = self.process_index(index)

        while count < self.keys:
            if(int(self.arr[index]) >= 1):
                count += 1
            else:
                break
            if(isinstance(key, str)):
                index = hashlib.md5(key.encode('utf-8'))
            else:
                index = hashlib.md5(key)
            index = index.hexdigest()
            index = int(index, 16)
            index = self.process_index(index)
        if count == self.keys:
            return True
        else:
            return False

    def process_index(self, index):
        if(index < 0):
            index += sys.maxsize
        if(index >= self.arr_size):
            index = index % self.arr_size
        return index
