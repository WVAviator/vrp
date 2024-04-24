from typing import Optional
from wgups.distance_table import DistanceTable
from wgups.package_table import PackageTable


class SavingsList:
    """
    A wrapper around a standard list which contains the savings gained by delivering two packages together rather than in separate trips to and from the hub. A key component of the Clarke-Wright Savings Algorithm. Can optionally provide a list of package IDs to limit the number of packages in the calculation.
    """

    def __init__(
        self,
        pt: PackageTable,
        dt: DistanceTable,
        priority_modifier: float = 0.0,
    ):
        self.pt = pt
        self.dt = dt

        self.savings_list = []
        self.package_list = pt.get_package_list()

        # O(n^2) - uses nested loops to compare each package to every other package to calculate the savings.
        for i in range(len(self.package_list)):
            for j in range(i + 1, len(self.package_list)):
                # We only care about packages that are ready to be delivered
                if (
                    self.package_list[i].status != "at the hub"
                    or self.package_list[j].status != "at the hub"
                ):
                    continue

                savings = self.calculate_savings(
                    self.package_list[i].package_id, self.package_list[j].package_id
                )

                # Priority is a modification to the base Clarke-Wright algorithm to prioritize packages with earlier deadlines.
                priority = 1
                if self.package_list[i].constraints.deadline < 1440.0:
                    priority += priority_modifier
                if self.package_list[j].constraints.deadline < 1440.0:
                    priority += priority_modifier

                self.savings_list.append(
                    (
                        savings * priority,
                        self.package_list[i].package_id,
                        self.package_list[j].package_id,
                    )
                )

        # The savings list is sorted by the amount of savings in descending order.
        # This will be used to determine which packages are best to deliver together first.
        self.savings_list.sort(key=lambda x: x[0], reverse=True)

    def calculate_savings(self, p1: int, p2: int) -> float:
        """
        Given two package ids that already exist in the initialized package table,
        calculates the savings that would be used in the savings report.
        """

        package1 = self.pt.get_package(p1)
        package2 = self.pt.get_package(p2)

        if package1 == None or package2 == None:
            raise Exception("Invalid package.")

        # Savings is the difference between two separate trips and one round trip:
        # (2hx + 2hy) - (hx + xy + hy)
        # Which can be algebraically simplified to hx + hy - xy
        # Where hx is the distance from the hub to point x, hy is the hub to point y, and xy is the distance from x to y
        savings = (
            self.dt.get_distance("HUB", package1.formatted_address())
            + self.dt.get_distance("HUB", package2.formatted_address())
            - self.dt.get_distance(
                package1.formatted_address(),
                package2.formatted_address(),
            )
        )

        return savings

    def __str__(self):
        formatted_savings_list = map(
            lambda x: f"{x[1]} <-> {x[2]}\t{x[0]:.2f}", self.savings_list
        )
        return "\n".join(formatted_savings_list)

    def __len__(self):
        return len(self.savings_list)

    def __getitem__(self, index):
        return self.savings_list[index]

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index < len(self.savings_list):
            result = self.savings_list[self.index]
            self.index += 1
            return result
        else:
            raise StopIteration
