from typing import Optional
from utilities.hash_table import HashTable
from wgups.distance_table import DistanceTable
from wgups.package_table import Package, PackageTable

AVERAGE_SPEED = 18
MAX_PACKAGES = 16
DUE_BACK_BUFFER = 15


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
        self.due_back_time = 1440.0
        self.priority = 0

    def set_due_back_time(self, time: float):
        """
        Updates the route's due back time which limits the route from being extended beyond that time, plus an additional buffer.
        """
        self.due_back_time = time + DUE_BACK_BUFFER

    def has_incomplete_group(self) -> Optional[int]:
        """
        Returns the group id if the route has a group of packages that are not all included in the route.
        """
        counts = HashTable()
        for p in self.deliveries:
            counts[p.group_id] = (counts[p.group_id] or 0) + 1
        for group_id, count in counts.items():
            if count < len(self.package_table.get_package_group(group_id)):
                return group_id
        return None

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
            package.status = "delivered"
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
            # print(
            #     "The paired package was interior to the route or missing from the route."
            # )
            return False

        if self.verify_deliveries(proposed_deliveries):
            self.deliveries = proposed_deliveries
            self.packages.add(package_id)
            if package.constraints.deadline < 1440.0:
                self.priority += self.calculate_priority(package)
            if include_paired:
                self.packages.add(paired_package_id)
                if paired_package.constraints.deadline < 1440.0:
                    self.priority += self.calculate_priority(paired_package)
            return True
        elif self.verify_deliveries(proposed_deliveries[::-1]):
            self.deliveries = proposed_deliveries[::-1]
            self.packages.add(package_id)
            if package.constraints.deadline < 1440.0:
                self.priority += self.calculate_priority(package)
            if include_paired:
                self.packages.add(paired_package_id)
                if paired_package.constraints.deadline < 1440.0:
                    self.priority += self.calculate_priority(paired_package)
            return True
        else:
            return False

    def calculate_priority(self, package: Package) -> float:
        """
        Calculates the priority value this package adds to the route. Packages with sooner deadlines will have higher priority.
        The priority is effectively the inverse of the time remaining to deliver this package.
        """
        time_remaining = package.constraints.deadline - self.departure_time
        return 1 / time_remaining if time_remaining > 0 else 0

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
            self.packages = self.packages.union(other.packages)
            self.priority += other.priority
            return True
        elif self.verify_deliveries(merged_deliveries[::-1]):
            self.deliveries = merged_deliveries[::-1]
            self.packages = self.packages.union(other.packages)
            self.priority += other.priority
            return True

        return False

    def calculate_distance(self, route: list[Package]) -> float:
        """
        Given a proposed route, calculate the total distance that the truck will travel.
        """
        distance = 0
        current = 0
        for package in route:
            distance += self.distance_table.get_package_distance(
                current, package.package_id
            )
            current = package.package_id
        distance += self.distance_table.get_package_distance(current, 0)
        return distance

    def calculate_time(self, route: list[Package]) -> float:
        """
        Given a proposed route, calculate the total time that the truck will travel.
        """
        return self.calculate_distance(route) / AVERAGE_SPEED * 60

    def verify_deliveries(self, proposed: list[Package]) -> bool:
        """
        A method used to determine whether a proposed route is legal. Given the package constraints.
        Does not check if grouped packages are together.
        """

        if len(proposed) > MAX_PACKAGES:
            # print("Proposed route contains too many packages.")
            return False

        proposed_route_finish_time = self.departure_time + self.calculate_time(proposed)

        if proposed_route_finish_time > self.due_back_time:
            # print(
            #     f"Proposed route finishes after due back time, at {self.route_finish_time()}."
            # )
            return False

        time = self.departure_time
        current = 0

        for package in proposed:

            # Verify correct truck
            if (
                package.constraints.required_truck
                and package.constraints.required_truck != self.truck_id
            ):
                # print(
                #     f"Proposed route violates truck restraint for package {package.package_id}"
                # )
                return False

            distance = self.distance_table.get_package_distance(
                current, package.package_id
            )
            time += distance / AVERAGE_SPEED * 60
            current = package.package_id

            # Verify arrives on time
            if time > package.constraints.deadline:
                # print(
                #     f"Proposed route violates deadline restraint for package {package.package_id}"
                # )
                return False

        # print("Proposed route is valid.")
        return True

    def route_distance(self) -> float:
        """
        Returns the total distance in miles that this route will travel.
        """
        return self.calculate_distance(self.deliveries)

    def route_finish_time(self) -> float:
        """
        Returns the time in minutes since midnight that this route will finish and the truck will have returned to the HUB.
        """
        route_time = self.calculate_time(self.deliveries)
        return self.departure_time + route_time

    def efficiency(self) -> float:
        """
        Returns the efficiency rating of this route, which is number of packages delivered divided by time.
        """
        route_time = self.route_finish_time() - self.departure_time
        efficiency = len(self.deliveries) / route_time
        # print(
        #     f"Calculated route efficiency for {len(self.deliveries)} packages delivered in {route_time} minutes: {efficiency}"
        # )
        return efficiency

    def __repr__(self):
        # HUB -> 1 -> 2 -> 3 -> HUB
        route_str = "HUB"
        for package in self.deliveries:
            route_str += f" -> {package.package_id}"
        route_str += " -> HUB"
        return route_str
