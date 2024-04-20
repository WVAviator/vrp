from wgups.distance_table import DistanceTable
from wgups.package_table import Package, PackageTable

AVERAGE_SPEED = 18


class Route:
    def __init__(
        self, departure_time: float, truck_id: int, dt: DistanceTable, pt: PackageTable
    ):
        self.deliveries: list[Package] = []
        self.packages = set()
        self.departure_time = departure_time
        self.truck_id = truck_id
        self.distance_table = dt
        self.package_table = pt
        self.has_simulated = False

    def simulate(self):
        """
        Simluates the package deliveries on this route. This method will add tracking details to every package that show them departing the HUB and when they are successfully delivered. No more packages can be added after a route is simulated.
        """
        if self.has_simulated:
            raise Exception("Attempt to simulate a route twice.")
        self.has_simulated = True

        time = self.departure_time
        current = 0
        for package in self.deliveries:
            package.add_tracking_info(
                self.departure_time, f"departed HUB on truck {self.truck_id}"
            )
            distance = self.distance_table.get_package_distance(
                current, package.package_id
            )
            time += distance / AVERAGE_SPEED * 60
            package.add_tracking_info(time, f"delivered to {package.address}")
            current = package.package_id

    def contains_package(self, package_id: int) -> bool:
        return package_id in self.packages

    def add_package(self, package_id: int, paired_package_id: int):
        """
        Given a package_id to potentially add to this route, as well as the paired_package_id which already exists in the route and results in savings, add the package to the route if no constraints are violated and the paired_package_id is not interior to the route. Returns True if the package was successfully added, or False otherwise.
        """

        if self.has_simulated:
            return False

        package = self.package_table.get_package(package_id)
        paired_package = self.package_table.get_package(paired_package_id)
        if package == None or paired_package == None:
            raise Exception("An invalid package ID was provided.")

        proposed_deliveries = []
        include_paired = False

        if len(self.deliveries) == 0:
            proposed_deliveries = [package, paired_package]
            include_paired = True
        elif self.deliveries[0].package_id == paired_package_id:
            proposed_deliveries = [package] + self.deliveries[::]
        elif self.deliveries[-1].package_id == paired_package_id:
            proposed_deliveries = self.deliveries[::] + [package]
        else:
            print(
                "The paired package was interior to the route or missing from the route."
            )
            return False

        if self.verify_deliveries(proposed_deliveries):
            self.deliveries = proposed_deliveries
            self.packages.add(package_id)
            if include_paired:
                self.packages.add(paired_package_id)
            return True
        elif self.verify_deliveries(proposed_deliveries[::-1]):
            self.deliveries = proposed_deliveries[::-1]
            self.packages.add(package_id)
            if include_paired:
                self.packages.add(paired_package_id)
            return True

        print("The proposed route was not valid.")
        return False

    def merge(self, other: "Route", p1_id: int, p2_id: int) -> bool:
        """
        Given this route and another route, as well as a package that exists in this route and a paired package that exists in the other, attempt to merge the two routes together. The merged route is added to this route. Returns True if the routes were successfully merged, and False otherwise.
        """

        if self.has_simulated or other.has_simulated:
            return False

        merged_deliveries = []

        if self.deliveries[-1] == p1_id or self.deliveries[-1] == p2_id:
            if other.deliveries[0] == p1_id or other.deliveries[0] == p2_id:
                merged_deliveries = self.deliveries + other.deliveries
            else:
                merged_deliveries = self.deliveries + other.deliveries[::-1]
        else:
            if other.deliveries[0] == p1_id or other.deliveries[0] == p2_id:
                merged_deliveries = self.deliveries[::-1] + other.deliveries
            else:
                merged_deliveries = other.deliveries + self.deliveries

        if self.verify_deliveries(merged_deliveries):
            self.deliveries = merged_deliveries
            self.packages.union(other.packages)
            return True
        elif self.verify_deliveries(merged_deliveries[::-1]):
            self.deliveries = merged_deliveries[::-1]
            self.packages.union(other.packages)
            return True

        return False

    def verify_deliveries(self, proposed: list[Package]):
        """
        A method used to determine whether a proposed route is legal. Given the package constraints.
        Does not check if grouped packages are together.
        """

        print("Verifying legality of route: ", proposed)

        time = self.departure_time
        current = 0

        for package in proposed:

            # Verify correct truck
            if (
                package.constraints.required_truck
                and package.constraints.required_truck != self.truck_id
            ):
                print(
                    f"Proposed route violates truck restraint for package {package.package_id}"
                )
                return False

            distance = self.distance_table.get_package_distance(
                current, package.package_id
            )
            time += distance / AVERAGE_SPEED * 60
            current = package.package_id

            # Verify arrives on time
            if time > package.constraints.deadline:
                print(
                    f"Proposed route violates deadline restraint for package {package.package_id}"
                )
                return False

        print("Proposed route is valid.")
        return True

    def route_finish_time(self) -> float:
        """
        Returns the time in minutes since midnight that this route will finish and the truck will have returned to the HUB.
        """
        time = self.departure_time
        current = 0
        for package in self.deliveries:
            distance = self.distance_table.get_package_distance(
                current, package.package_id
            )
            time += distance / AVERAGE_SPEED * 60
            current = package.package_id

        time += (
            self.distance_table.get_package_distance(current, 0) / AVERAGE_SPEED * 60
        )
        return time

    def efficiency(self) -> float:
        """
        Returns the efficiency rating of this route, which is number of packages delivered divided by time.
        """
        route_time = self.route_finish_time() - self.departure_time
        return len(self.deliveries) / route_time
