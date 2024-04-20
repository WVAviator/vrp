from wgups.package import Package
from wgups.route import Route


class Truck:
    def __init__(self, id: int) -> None:
        self.id = id
        self.routes: list[Route] = []
        self.next_available_time: float = 480.0
        self.packages: list[Package] = []

    def add_route(self, route: Route) -> None:
        self.routes.append(route)
        route.simulate()
        self.next_available_time = route.route_finish_time()
        self.packages.extend(route.deliveries)

    def total_distance_travelled(self) -> float:
        return sum(
            [route.calculate_distance(route.deliveries) for route in self.routes]
        )
