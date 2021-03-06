from persistent import *
from persistent.list import PersistentList as ZL

class MRUCache(Persistent):
    def __init__(self, size):
        self.cache = ZL([])
        self.size = size

    def add(self, val):
        self.delete(val)
        self.cache.append(val)
        
        if len(self.cache) > self.size:
            self.cache = self.cache[-self.size:]

    def delete(self, val):
        try:
            self.cache.remove(val)
        except ValueError:
            pass

    def top(self, num):
        ret = self.cache[-num:]
        ret.reverse()
        return ret

    def __repr__(self):
        return str(self.cache[:self.size])
