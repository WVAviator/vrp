import csv

from utilities.hash_table import HashTable
from wgups.package_table import PackageTable


class DistanceTable:
    def get_distance(self, addr1: str, addr2: str) -> float:
        """
        Given two formatted addresses (Street + Zip Code), this returns the distance between them through a distance table lookup.
        """
        a1_index = self.address_table.get(addr1)
        a2_index = self.address_table.get(addr2)

        if a1_index == None:
            raise Exception(f"Address not found: {addr1}")
        if a2_index == None:
            raise Exception(f"Address not found: {addr2}")

        # The first index should be the largest since only the bottom-left of the distance table is populated with values.
        if a1_index < a2_index:
            a1_index, a2_index = a2_index, a1_index

        return self.distance_table[a1_index][a2_index]

    def get_address(self, index: int) -> str:
        """
        Given an index, retuns the formatted address.
        """
        return self.address_index_table[index]

    def get_address_index(self, address: str) -> int:
        """
        Given a formatted address, returns the address ID for use in distance table lookups
        """
        addr = self.address_table.get(address)
        if addr == None:
            raise Exception(f"Address not found: {address}")
        return addr

    def get_package_distance(self, pid1: int, pid2: int):
        """
        Given two package IDs, returns the distance between the package delivery addresses.
        """
        p1 = self.package_table.get_package(pid1)
        p2 = self.package_table.get_package(pid2)

        addr1 = p1.formatted_address() if p1 != None else "HUB"
        addr2 = p2.formatted_address() if p2 != None else "HUB"

        return self.get_distance(addr1, addr2)

    def __init__(self, file_path: str, package_table: PackageTable) -> None:
        self.package_table = package_table
        self.address_table: HashTable[str, int] = HashTable()
        self.address_index_table = []
        self.distance_table = []

        # Builds the distance table from the CSV file
        with open(file_path) as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=",")

            for i, row in enumerate(csv_reader):
                address = " ".join("".join(row[1].split("\n")).strip().split("("))[:-1]

                # Trimming the last ")" character off the addresses messing up the HUB address
                if address == "HU":
                    address = "HUB"

                self.address_table.insert(address, i)
                self.address_index_table.append(address)

                values = []

                for j in range(2, len(row)):
                    value = float(row[j]) if row[j] != "" else 0.0
                    values.append(value)

                self.distance_table.append(values)
