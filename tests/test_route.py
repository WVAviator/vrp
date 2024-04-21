from wgups.distance_table import DistanceTable
from wgups.package_table import PackageTable
from wgups.route import Route


def test_route_instantiation():
    pt = PackageTable("resources/WGUPS Package File.csv")
    dt = DistanceTable("resources/WGUPS Distance Table.csv", pt)

    route = Route(480.0, 1, dt, pt)

    assert route.add_package(1, 2) == True


def test_route_normal_add():
    pt = PackageTable("resources/WGUPS Package File.csv")
    dt = DistanceTable("resources/WGUPS Distance Table.csv", pt)

    route = Route(480.0, 1, dt, pt)

    assert route.add_package(1, 2) == True
    assert route.add_package(4, 1) == True
    assert len(route.deliveries) == 3


def test_route_time_calculation():
    pt = PackageTable("resources/WGUPS Package File.csv")
    dt = DistanceTable("resources/WGUPS Distance Table.csv", pt)

    route = Route(480.0, 1, dt, pt)
    assert route.add_package(1, 2) == True

    # HUB -> 1 = 3.5, 1 -> 2 = 1.5, 2 -> HUB = 2.8, Total = 7.8, @ 18MPH should be 26 minutes
    assert route.route_finish_time() == 480 + 26


def test_deadline_constraint():
    pt = PackageTable("resources/WGUPS Package File.csv")
    dt = DistanceTable("resources/WGUPS Distance Table.csv", pt)

    # Package 1 has 10:30 AM (630) deadline

    route = Route(630.0, 1, dt, pt)
    assert route.add_package(1, 2) == False


def test_truck_constraint():
    pt = PackageTable("resources/WGUPS Package File.csv")
    dt = DistanceTable("resources/WGUPS Distance Table.csv", pt)

    route = Route(480.0, 1, dt, pt)

    # Package 3 can only be on Truck 2
    assert route.add_package(1, 3) == False


def test_simulate_package_tracking():
    pt = PackageTable("resources/WGUPS Package File.csv")
    dt = DistanceTable("resources/WGUPS Distance Table.csv", pt)

    route = Route(480.0, 1, dt, pt)

    assert route.add_package(1, 2) == True

    package1 = pt.get_package(1)
    assert package1 != None

    assert len(package1.tracking_info) == 0

    route.simulate()

    assert len(package1.tracking_info) == 2


def test_route_merge():
    pt = PackageTable("resources/WGUPS Package File.csv")
    dt = DistanceTable("resources/WGUPS Distance Table.csv", pt)

    route1 = Route(480.0, 1, dt, pt)
    route2 = Route(480.0, 1, dt, pt)

    route1.add_package(2, 4)
    route2.add_package(5, 7)

    assert route1.merge(route2, 4, 5) == True
    assert len(route1.deliveries) == 4


def test_route_reversible():
    pt = PackageTable("resources/WGUPS Package File.csv")
    dt = DistanceTable("resources/WGUPS Distance Table.csv", pt)

    # Package 1 has 10:30 AM (630) deadline and is 3.5 miles from HUB (11.67 minutes)
    # If added to back of route, would be added too late, but route can be reversed

    route = Route(615.0, 1, dt, pt)
    assert route.add_package(4, 2) == True
    assert route.add_package(1, 2) == True

    # The same route should fail if even reversing isn't enough.

    route2 = Route(620.0, 1, dt, pt)
    assert route2.add_package(4, 2) == True
    assert route2.add_package(1, 2) == False


def test_route_contains():
    pt = PackageTable("resources/WGUPS Package File.csv")
    dt = DistanceTable("resources/WGUPS Distance Table.csv", pt)

    route = Route(480.0, 1, dt, pt)
    assert route.add_package(1, 2) == True

    assert route.contains_package(1) == True
    assert route.contains_package(2) == True
    assert route.contains_package(3) == False


def test_route_efficiency():
    pt = PackageTable("resources/WGUPS Package File.csv")
    dt = DistanceTable("resources/WGUPS Distance Table.csv", pt)

    route1 = Route(480.0, 1, dt, pt)
    route2 = Route(480.0, 1, dt, pt)

    # These are close together and close to the hub, very efficient
    route1.add_package(21, 19)
    # These are far apart opposite the HUB, very inefficient
    route2.add_package(15, 6)

    assert route1.efficiency() > route2.efficiency()


def test_remaining_group_packages():
    pt = PackageTable("resources/WGUPS Package File.csv")
    dt = DistanceTable("resources/WGUPS Distance Table.csv", pt)

    route = Route(480.0, 1, dt, pt)

    # There are six packages in the group: 13, 14, 15, 16, 19, 20
    assert route.add_package(13, 19)

    assert route.remaining_in_group(13, route.deliveries) == 4


def test_has_incomplete_group():
    pt = PackageTable("resources/WGUPS Package File.csv")
    dt = DistanceTable("resources/WGUPS Distance Table.csv", pt)

    route = Route(480.0, 1, dt, pt)

    assert route.add_package(1, 2)
    assert not route.has_incomplete_group()
    assert route.has_incomplete_group() == None

    assert route.add_package(19, 2)
    possible_group_ids = [13, 14, 15, 16, 19, 20]
    assert route.has_incomplete_group()
    assert route.has_incomplete_group() in possible_group_ids


def test_insert_package():
    pt = PackageTable("resources/WGUPS Package File.csv")
    dt = DistanceTable("resources/WGUPS Distance Table.csv", pt)

    route = Route(480.0, 2, dt, pt)

    # Packages 1 and 17 form a standard route, but package 40 falls directly between them
    # Packages 7 and 18 create a wider arc
    # The insertion should logically occur between 1 and 17
    assert route.add_package(1, 17)
    assert route.add_package(7, 1)
    assert route.add_package(14, 17)
    assert route.insert_package(40)

    # route should be 1 -> 17 -> 40 -> 7 -> 18
    print(route)
    assert route.deliveries[2].package_id == 40


def test_calculate_distance():
    pt = PackageTable("resources/WGUPS Package File.csv")
    dt = DistanceTable("resources/WGUPS Distance Table.csv", pt)

    route = Route(480.0, 2, dt, pt)
    assert route.add_package(1, 2)

    assert route.calculate_distance(route.deliveries) == 7.8
