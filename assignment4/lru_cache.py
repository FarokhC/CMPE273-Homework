from pickle_hash import serialize_GET, serialize_PUT, serialize_DELETE

class lru_cache():
    def __init__(self, *args, **kwargs):
        self.keys = args[0]
        self.cache = []

    def __call__(self, *args, **kwargs):
        def wrapper(*args2):
            three_params = True
            keys = args2[0]
            try:
                data_bytes = args2[1]
                hash_code = args2[2]

            except:
                print("one params passed")
                three_params = False

            func = args[0]
            data_bytes, key = serialize_GET(keys)
            data = self.get_lru_cache(key)

            if(data != False):
                print("Local LRU Cache Response: " + str(data))
                self.add_to_lru_cache(key)
                return data
            else:
                res = None
                if(three_params):
                    print("key: " + str(key))
                    print("self.data_bytes: " + str(data_bytes))
                    print("self.hashcode: " + str(hash_code))
                    res = func(keys, data_bytes, hash_code)
                else:
                    res = func(keys)
                self.add_to_lru_cache(key)
                return res

            return func(key)
        return wrapper

    def add_to_lru_cache(self, data):
        if(len(self.cache) >= self.keys):
            if(len(self.cache) > 0):
                self.cache.pop(0)
        self.cache.append(data)

    def get_lru_cache(self, data):
        for i in range (0, len(self.cache)):
            if(self.cache[i] == data):
                return self.cache[i]
        return False

