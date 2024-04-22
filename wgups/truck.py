from wgups.package import Package
from wgups.route import Route


class Truck:
    def __init__(self, id: int) -> None:
        self.id = id
        self.routes: list[Route] = []
        self.next_available_time: float = 480.0
        self.packages: list[Package] = []

    def add_route(self, route: Route) -> None:
        """
        Adds a route to this truck. Adding a route also simulates the route and updates the truck's next_available_time with the time it arrives back at the hub.
        """
        self.routes.append(route)
        route.simulate()
        self.next_available_time = route.route_finish_time()
        self.packages.extend(route.deliveries)

    def total_distance_travelled(self) -> float:
        """
        Returns the total distance this truck has travelled since starting the day.
        """
        return sum(
            [route.calculate_distance(route.deliveries) for route in self.routes]
        )

    def last_route_finish_time(self) -> float:
        """
        Returns the finish time of the last route this truck completed.
        """
        if not self.routes:
            return 0.0
        return self.routes[-1].route_finish_time()
