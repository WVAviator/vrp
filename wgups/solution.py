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
