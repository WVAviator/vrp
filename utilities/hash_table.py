from typing import TypeVar, Generic, List, Tuple, Optional

V = TypeVar('V')

class HashTable(Generic[V]):
    def __init__(self):
        self.size = 40
        self.table: List[List[Tuple[int, V]]] = [[]] * self.size

    def hash(self, key: int):
        hash_value = key % self.size
        return hash_value

    def insert(self, key: int, value: V):
        hash_value = self.hash(key)
        if self.table[hash_value] is None:
            self.table[hash_value] = [(key, value)]
        else:
            self.table[hash_value].append((key, value))

    def get(self, key: int) -> Optional[V]:
        hash_value = self.hash(key)
        if self.table[hash_value] is None:
            return None
        else:
            for item in self.table[hash_value]:
                if item[0] == key:
                    return item[1]
            return None

    def remove(self, key: int):
        hash_value = self.hash(key)
        if self.table[hash_value] is not None:
            for index, item in enumerate(self.table[hash_value]):
                if item[0] == key:
                    self.table[hash_value].pop(index)
                    return
