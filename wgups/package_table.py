from utilities.hash_table import HashTable
from wgups.package import Package
from typing import Optional
import csv


class PackageTable:
    def __init__(self, package_file_path: str):
        self.package_table: HashTable[int, Package] = HashTable()
        self.package_list: list[Package] = []
        self._load_package_data(package_file_path)

    def get_package(self, package_id: int) -> Optional[Package]:
        """
        Returns the package object with the given package_id
        """
        return self.package_table.get(package_id)

    def get_package_list(self) -> list[Package]:
        """
        Returns a full list of packages
        """
        return self.package_list

    def get_undelivered_packages(self) -> list[Package]:
        """
        Returns a list of packages that have not yet been delivered
        """
        return [
            package for package in self.package_list if package.status != "delivered"
        ]

    def get_package_group(self, package_id: int) -> list[int]:
        """
        For packages that must be delivered with others, this returns a list of all the packages together that should be added to a single route.
        """
        package = self.get_package(package_id)
        if package is None:
            return []

        return [
            p.package_id for p in self.package_list if p.group_id == package.group_id
        ]

    def next_package_arrival(self) -> float:
        """
        This returns the time that the next package should be arriving at the hub ready for delivery.
        """
        delayed_packages = [1440.0] + [
            p.constraints.delayed_until
            for p in self.package_list
            if p.status == "delayed"
        ]
        return min(delayed_packages)

    def update_statuses(self, time: float):
        """
        This updates the package statuses based on the provided time. Useful for determining when delayed packages have finally arrived to the hub and updating their status so that they may appear in the savings lists.
        """
        for package in self.package_list:
            if (
                package.status == "delayed"
                and time >= package.constraints.delayed_until
            ):
                package.status = "at the hub"
                package.add_tracking_info(
                    package.constraints.delayed_until, "Arrived at the hub"
                )
                if package.constraints.updated_address != "":
                    package.address = package.constraints.updated_address
                    package.zip_code = package.constraints.updated_zip_code

    def packages_remaining(self) -> int:
        """
        Returns the number of packages that have not yet been delivered
        """
        return len(self.get_undelivered_packages())

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

        # Some packages have paired packages that must be grouped together by their group id
        # This is a union find problem
        def find(package_id: int) -> int:
            package = self.get_package(package_id)
            assert package is not None

            if package.group_id == package_id:
                return package_id
            package.group_id = find(package.group_id)
            return package.group_id

        def union(p1: int, p2: int):
            group1 = find(p1)
            group2 = find(p2)
            if group1 != group2:
                package1 = self.get_package(group1)
                package2 = self.get_package(group2)
                assert package1 is not None and package2 is not None
                package1.group_id = group2

        for package in self.package_list:
            for paired_package in package.constraints.paired_packages:
                union(package.package_id, paired_package)

        for package in self.package_list:
            find(package.package_id)

        print(f"Loaded {len(self.package_list)} packages")
