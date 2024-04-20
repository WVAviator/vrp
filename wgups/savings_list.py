from wgups.distance_table import DistanceTable
from wgups.package_table import PackageTable

# Determines the savings multiplier for routes with priority packages
PRIORITY_MODIFIER = 0.0


class SavingsList:
    """
    A wrapper around a standard list which contains the savings gained by delivering two packages together rather than in separate trips to and from the hub. A key component of the Clarke-Wright Savings Algorithm.
    """

    def __init__(self, pt: PackageTable, dt: DistanceTable):
        self.savings_list = []
        package_list = pt.get_package_list()

        # O(n^2) - uses nested loops to compare each package to every other package to calculate the savings.
        for i in range(len(package_list)):
            for j in range(i + 1, len(package_list)):
                if (
                    package_list[i].status != "at the hub"
                    or package_list[j].status != "at the hub"
                ):
                    continue

                # Savings is the difference between two separate trips and one round trip:
                # (2hx + 2hy) - (hx + xy + hy)
                # Which can be algebraically simplified to hx + hy - xy
                # Where hx is the distance from the hub to point x, hy is the hub to point y, and xy is the distance from x to y
                savings = (
                    dt.get_distance("HUB", package_list[i].formatted_address())
                    + dt.get_distance("HUB", package_list[j].formatted_address())
                    - dt.get_distance(
                        package_list[i].formatted_address(),
                        package_list[j].formatted_address(),
                    )
                )

                # Priority is a modification to the base Clarke-Wright algorithm to prioritize packages with earlier deadlines.
                priority = 1
                if package_list[i].constraints.deadline < 1440.0:
                    priority += PRIORITY_MODIFIER
                if package_list[j].constraints.deadline < 1440.0:
                    priority += PRIORITY_MODIFIER

                self.savings_list.append(
                    (
                        savings * priority,
                        package_list[i].package_id,
                        package_list[j].package_id,
                    )
                )

        # The savings list is sorted by the amount of savings in descending order.
        # This will be used to determine which packages are best to deliver together first.
        self.savings_list.sort(key=lambda x: x[0], reverse=True)

    def __str__(self):
        formatted_savings_list = map(
            lambda x: f"{x[1]} <-> {x[2]}\t{x[0]}", self.savings_list
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
