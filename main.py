from wgups.distance_table import DistanceTable
from wgups.package_table import PackageTable
from wgups.route import Route
from wgups.savings_list import SavingsList
from wgups.truck import Truck

# The minimum savings required to consider delivering two packages together
SAVINGS_ALPHA = 1


pt = PackageTable("resources/WGUPS Package File.csv")
dt = DistanceTable("resources/WGUPS Distance Table.csv", pt)


# savings_list = SavingsList(pt, dt)
# print(savings_list)

# for _, p1, p2 in savings_list:
#     pass

truck1 = Truck(1)
truck2 = Truck(2)
# Only two drivers are available, so truck 3 is never used
# truck3 = Truck(3)

trucks_at_hub = [truck1, truck2]

# while there are packages remaining to be delivered
while pt.packages_remaining() > 0:

    # for the next available truck at the hub
    trucks_at_hub.sort(key=lambda x: x.next_available_time)
    current_truck = trucks_at_hub[0]

    # update package statuses
    pt.update_statuses(current_truck.next_available_time)

    print(
        f"Truck {current_truck.id} is next available at HUB for loading at {current_truck.next_available_time}"
    )

    # generate a new savings list with the packages currently at the hub
    savings_list = SavingsList(pt, dt)

    print(f"Generated a savings list containing {len(savings_list)} possible routings")

    # generate routes from the savings list and package constraints
    assigned_packages = set()
    candidate_routes = []

    # if we know there are delayed packages inbound to the hub, we should schedule routes that return to the hub by this time
    # if a truck returns a few minutes early, it will be unable to depart with more packages and end up waiting
    due_back_time = pt.next_package_arrival()

    for savings, p1, p2 in savings_list:

        if savings <= SAVINGS_ALPHA:
            break
        if p1 not in assigned_packages and p2 not in assigned_packages:
            new_route = Route(
                current_truck.next_available_time, current_truck.id, dt, pt
            )
            new_route.set_due_back_time(due_back_time)

            if new_route.add_package(p1, p2):
                print(f"Creating new candidate route for packages {p1} and {p2}")

                candidate_routes.append(new_route)
                assigned_packages.add(p1)
                assigned_packages.add(p2)

        elif p1 in assigned_packages and p2 not in assigned_packages:
            for route in candidate_routes:
                if route.contains_package(p1):
                    if route.add_package(p2, p1):
                        print(
                            f"Adding package {p2} to existing route with package {p1}"
                        )
                        assigned_packages.add(p2)
                    break
        elif p1 not in assigned_packages and p2 in assigned_packages:
            for route in candidate_routes:
                if route.contains_package(p2):
                    if route.add_package(p1, p2):
                        print(
                            f"Adding package {p1} to existing route with package {p2}"
                        )
                        assigned_packages.add(p1)
                    break
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
                print(f"Merging routes {route1_index} and {route2_index}")
                candidate_routes.pop(route2_index)

    if len(candidate_routes) == 0:
        print("No candidate routes to consider at this time, truck will wait")
        current_truck.next_available_time = due_back_time
        if current_truck.next_available_time >= 1440:
            print("End of day reached, stopping simulation")
            break
        continue

    # select the best route (routes with higher priority (sooner deadlines) will be preferred)
    # routes with incomplete package groups will be ignored
    candidate_routes.sort(key=lambda x: (x.priority, x.efficiency()), reverse=True)
    best_route_index = 0
    for i, route in enumerate(candidate_routes):
        if not route.has_incomplete_group():
            best_route_index = i
            break

    # simulate the route (update package tracking info) and update the truck next available time
    print(
        f"Truck {current_truck.id} will depart at {current_truck.next_available_time} with {len(candidate_routes[0].deliveries)} packages and an estimated return time of {candidate_routes[0].route_finish_time()}"
    )
    current_truck.add_route(candidate_routes[0])


if pt.packages_remaining() > 0:
    print("Failed to deliver all packages.")
    print(f"Total remaining packages: {pt.packages_remaining()}")
    print("Undelivered packages: ", pt.get_undelivered_packages())
else:
    print("All packages delivered!")
    final_time = max([truck.next_available_time for truck in trucks_at_hub])
    print(
        f"All packages delivered by: {(final_time / 60):02.0f}:{(final_time % 60):02.0f}"
    )
    print(
        f"Total distance travelled: {sum([truck.total_distance_travelled() for truck in trucks_at_hub]):.2f} miles"
    )
