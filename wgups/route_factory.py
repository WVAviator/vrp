from wgups.distance_table import DistanceTable
from wgups.package_table import PackageTable
from wgups.route import Route
from wgups.savings_list import SavingsList
from wgups.truck import Truck

SAVINGS_ALPHA = 0


class RouteFactory:
    def __init__(self, pt: PackageTable, dt: DistanceTable):
        self.pt = pt
        self.dt = dt

    def compute_routes(self, savings_list: SavingsList, current_truck: Truck):

        # generate routes from the savings list and package constraints
        assigned_packages = set()
        candidate_routes = []

        # if we know there are delayed packages inbound to the hub, we should schedule routes that return to the hub by this time
        # this is necessary because those delayed packages may have deadlines and a truck should be waiting for them
        # if a truck returns a few minutes early, it will be unable to depart with more packages and end up waiting
        due_back_time = self.pt.next_package_arrival()

        for savings, p1, p2 in savings_list:

            # we don't need to waste time checking additions to the route that don't provide enough savings
            # sometimes more trips to the hub will result in better routes
            if savings <= SAVINGS_ALPHA:
                break

            # case where neither package is assigned to a potential route yet
            if p1 not in assigned_packages and p2 not in assigned_packages:
                new_route = Route(
                    current_truck.next_available_time,
                    current_truck.id,
                    self.dt,
                    self.pt,
                )
                new_route.set_due_back_time(due_back_time)

                if new_route.add_package(p1, p2):
                    candidate_routes.append(new_route)
                    assigned_packages.add(p1)
                    assigned_packages.add(p2)

            # case where package 1 is already assigned a route and package 2 is not
            # we should try to add package 2 to the same route if so
            elif p1 in assigned_packages and p2 not in assigned_packages:
                for route in candidate_routes:
                    if route.contains_package(p1):
                        if route.add_package(p2, p1):
                            assigned_packages.add(p2)
                        break

            # case where package 2 is already assigned a route and package 1 is not
            # we should try to add package 1 to the same route if so
            elif p1 not in assigned_packages and p2 in assigned_packages:
                for route in candidate_routes:
                    if route.contains_package(p2):
                        if route.add_package(p1, p2):
                            assigned_packages.add(p1)
                        break

            # case where both packages are already assigned to separate routes
            # we should try to merge the routes if possible
            elif p1 in assigned_packages and p2 in assigned_packages:
                route1_index = 0
                route2_index = 0
                for i, route in enumerate(candidate_routes):
                    if route.contains_package(p1):
                        route1_index = i
                    if route.contains_package(p2):
                        route2_index = i
                if route1_index == route2_index:
                    continue

                if candidate_routes[route1_index].merge(
                    candidate_routes[route2_index], p1, p2
                ):
                    candidate_routes.pop(route2_index)

        return candidate_routes
