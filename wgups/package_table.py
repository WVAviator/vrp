from utilities.hash_table import HashTable
from typing import cast, Optional
import csv


class Package:
    def __init__(
        self,
        package_id: int,
        address: str,
        deadline: str,
        city: str,
        zip_code: str,
        weight: int,
        note: str,
    ):
        self.package_id = package_id
        self.address = address
        self.deadline = deadline
        self.city = city
        self.zip_code = zip_code
        self.weight = weight
        self.note = note
        self.status = "at the hub"


class PackageTable:
    def __init__(self, package_file_path: str):
        self.package_table: HashTable[int, Package] = HashTable()
        self._load_package_data(package_file_path)

    def get_package(self, package_id: int) -> Optional[Package]:
        return self.package_table.get(package_id)

    def _load_package_data(self, file_path: str):
        with open(file_path) as csvfile:
            list_reader = csv.reader(csvfile, delimiter=",")
            for row in list_reader:

                package_id = int(row[0])
                address = row[1]
                deadline = row[5]
                city = row[2]
                zip_code = row[4]
                weight = int(row[6])
                note = row[7]

                package = Package(
                    package_id, address, deadline, city, zip_code, weight, note
                )

                self.package_table.insert(package_id, package)
