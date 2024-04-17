from wgups.package_table import Package


class Route:
    def __init__(self, departure_time: int, truck_id: int):
        self.deliveries = []
        self.departure_time = departure_time
        self.truck_id = truck_id

    def can_deliver(self, package: Package):
        pass
