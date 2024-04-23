from utilities.time import time_float_to_str
from wgups.truck import Truck


class Solution:
    def __init__(self, trucks: list[Truck]):
        self.trucks = trucks.copy()
        self.total_distance = sum([t.total_distance_travelled() for t in trucks])

    def __repr__(self):
        final_time = max([t.last_route_finish_time() for t in self.trucks])
        s = f"All packages delivered by: {time_float_to_str(final_time)}\n"
        s += f"Total distance travelled: {self.total_distance:.2f} miles\n"
        return s

    def print_routes(self):
        """
        Pretty-prints the route information for all trucks.
        """
        for t in self.trucks:
            print(f"Truck {t.id}:")
            for r in t.routes:
                print(
                    f"Depart: {time_float_to_str(r.departure_time)} | Arrive: {time_float_to_str(r.route_finish_time())}\n{r}"
                )
            print("\n")

    def print_truck_info(self, truck_id: int) -> bool:
        """
        Pretty-prints the information for the provided truck_id.
        """
        for t in self.trucks:
            if t.id == truck_id:
                t.print_truck_info()
                return True
        return False

    def print_package_info(self, package_id: int, time: float = 1440.0):
        """
        Pretty-prints package tracking information given a package_id and optional time.
        """
        for t in self.trucks:
            for r in t.routes:
                for p in r.deliveries:
                    if p.package_id == package_id:
                        print(f"==== Package {package_id} ====\n")
                        for info in p.get_tracking_info(time):
                            print(info)
                        print("\n====================\n")
                        return True
        return False
