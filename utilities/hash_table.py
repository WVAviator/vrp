from typing import TypeVar, Generic, List, Tuple, Optional, Hashable

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


class HashTable(Generic[K, V]):
    def __init__(self):
        self.size = 40
        self.table: List[List[Tuple[K, V]]] = [[]] * self.size
        self.length = 0

    def hash(self, key: K):
        hash_value = hash(key) % self.size
        return hash_value

    def insert(self, key: K, value: V):
        hash_value = self.hash(key)
        if self.table[hash_value] is None:
            self.table[hash_value] = [(key, value)]
        else:
            self.table[hash_value].append((key, value))
        self.length += 1

    def get(self, key: K) -> Optional[V]:
        hash_value = self.hash(key)
        if self.table[hash_value] is None:
            return None
        else:
            for item in self.table[hash_value]:
                if item[0] == key:
                    return item[1]
            return None

    def remove(self, key: K):
        hash_value = self.hash(key)
        if self.table[hash_value] is not None:
            for index, item in enumerate(self.table[hash_value]):
                if item[0] == key:
                    self.table[hash_value].pop(index)
                    self.length -= 1
                    return
