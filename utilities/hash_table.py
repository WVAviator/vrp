class HashTable:
    def __init__(self):
        self.size = 40
        self.table = [[]] * self.size

    def hash(self, key):
        hash_value = hash(key) % self.size
        return hash_value

    def insert(self, key, value):
        hash_value = self.hash(key)
        if self.table[hash_value] is None:
            self.table[hash_value] = [(key, value)]
        else:
            self.table[hash_value].append((key, value))

    def get(self, key):
        hash_value = self.hash(key)
        if self.table[hash_value] is None:
            return None
        else:
            for item in self.table[hash_value]:
                if item[0] == key:
                    return item[1]
            return None

    def remove(self, key):
        hash_value = self.hash(key)
        if self.table[hash_value] is not None:
            for index, item in enumerate(self.table[hash_value]):
                if item[0] == key:
                    self.table[hash_value].pop(index)
                    return
