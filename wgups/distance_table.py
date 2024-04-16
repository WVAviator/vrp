import csv

from utilities.hash_table import HashTable


class DistanceTable:
    def get_distance(self, addr1: str, addr2: str) -> float:
        a1_index = self.address_table.get(addr1)
        a2_index = self.address_table.get(addr2)

        if a1_index == None or a2_index == None:
            raise Exception("Address not found.")

        if a1_index < a2_index:
            a1_index, a2_index = a2_index, a1_index

        return self.distance_table[a1_index][a2_index]

    def __init__(self, file_path: str) -> None:
        self.address_table: HashTable[str, int] = HashTable()
        self.distance_table = []

        with open(file_path) as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=",")

            for i, row in enumerate(csv_reader):
                address = " ".join("".join(row[1].split("\n")).strip().split("("))[:-1]
                if address == "HU":
                    address = "HUB"

                self.address_table.insert(address, i)

                values = []

                for j in range(2, len(row)):
                    value = float(row[j]) if row[j] != "" else 0.0
                    values.append(value)

                self.distance_table.append(values)
