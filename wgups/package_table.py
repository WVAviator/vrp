from utilities.hash_table import HashTable
from wgups.package import Package
from typing import Optional
import csv


class PackageTable:
    def __init__(self, package_file_path: str):
        self.package_table: HashTable[int, Package] = HashTable()
        self.package_list = []
        self._load_package_data(package_file_path)

    def get_package(self, package_id: int) -> Optional[Package]:
        return self.package_table.get(package_id)

    def get_package_list(self) -> list[Package]:
        return self.package_list

    def update_statuses(self, time: float):
        for package in self.package_list:
            if (
                package.status == "delayed"
                and time >= package.constraints.delayed_until
            ):
                package.status = "at the hub"

    def packages_remaining(self) -> int:
        count = len(self.package_list)
        for package in self.package_list:
            if package.status != "delivered":
                count -= 1
        return count

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
                self.package_list.append(package)
