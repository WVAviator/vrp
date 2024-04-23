from typing import Optional
from utilities.time import time_float_to_str
from wgups.distance_table import DistanceTable
from wgups.package_table import PackageTable
from wgups.route import Route
from wgups.route_factory import RouteFactory
from wgups.savings_list import SavingsList
from wgups.solution import Solution
from wgups.truck import Truck


class SolutionFactory:

    def __init__(self):
        pass

    def generate_best_solution(self):
        """
        Tries multiple different values for the priority_modifier variable used when generate savings lists for the Clarke Wright algorithm. Returns the best solve.
        """
        best_solution = None

        priority_modifier = 0.00
        while priority_modifier <= 2.0:
            solution = self.generate_solution(priority_modifier)
            priority_modifier += 0.01

            if solution == None:
                continue

            if best_solution == None:
                best_solution = solution
            elif solution.total_distance < best_solution.total_distance:
                best_solution = solution

        return best_solution

    def generate_solution(self, priority_modifier) -> Optional[Solution]:
        """
        Generates a solution based on the provided priority_modifier variable (which affects the weight of priority packages in the savings list generation)
        """
        pt = PackageTable("resources/WGUPS Package File.csv")
        dt = DistanceTable("resources/WGUPS Distance Table.csv", pt)

        truck1 = Truck(1)
        truck2 = Truck(2)
        # Only two drivers are available, so truck 3 is never used
        truck3 = Truck(3)

        trucks_at_hub = [truck1, truck2]

        route_factory = RouteFactory(pt, dt)

        # while there are packages remaining to be delivered
        while pt.packages_remaining() > 0:

            # for the next available truck at the hub
            trucks_at_hub.sort(key=lambda x: x.next_available_time)
            current_truck = trucks_at_hub[0]

            # update package statuses
            pt.update_statuses(current_truck.next_available_time)

            print(
                f"Truck {current_truck.id} is next available at HUB for loading at {time_float_to_str(current_truck.next_available_time)}"
            )

            # generate a new savings list with the packages currently at the hub
            savings_list = SavingsList(pt, dt, priority_modifier)

            print(
                f"Generated a savings list containing {len(savings_list)} possible routings"
            )

            candidate_routes = route_factory.compute_routes(savings_list, current_truck)

            # if no candidate routes are available, the truck will wait until the next package arrives
            # the due_back_time is a good interval because it represents the next time the number of packages may change
            if len(candidate_routes) == 0:
                print("No candidate routes to consider at this time, truck will wait")
                current_truck.next_available_time = pt.next_package_arrival()
                # in the case where the due_back_time is the end of the day, there will be no more packages inbound, we can stop
                if current_truck.next_available_time >= 1440:
                    print("End of day reached, stopping simulation")
                    break
                continue

            # select the best route (routes with higher priority (sooner deadlines) will be preferred)
            candidate_routes.sort(
                key=lambda x: (x.priority, x.efficiency()), reverse=True
            )

            # simulate the route (update package tracking info) and update the truck next available time
            print(
                f"Truck {current_truck.id} will depart at {time_float_to_str(current_truck.next_available_time)} with {len(candidate_routes[0].deliveries)} packages and an estimated return time of {time_float_to_str(candidate_routes[0].route_finish_time())}"
            )
            current_truck.add_route(candidate_routes[0])

        if pt.packages_remaining() > 0:
            return None

        solution = Solution([truck1, truck2, truck3])
        return solution
