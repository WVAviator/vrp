from utilities.time import time_float_to_str
from wgups.distance_table import DistanceTable
from wgups.package_table import PackageTable
from wgups.route import Route
from wgups.route_factory import RouteFactory
from wgups.savings_list import SavingsList
from wgups.truck import Truck
from wgups.solution_factory import SolutionFactory

solution_factory = SolutionFactory()

best_solution = solution_factory.generate_best_solution()

print(best_solution)

state = ""

while state != "q":
    if state == "p":
        print(
            "To track a package, enter the time (00:00-24:00) and the package ID separated by a space. Enter 'b' to go back."
        )
        print("Example viewing tracking info for package 26 at 10:15 AM:\n\t10:15 26")
        user_input = input()
        if user_input == "b":
            state = ""
            continue
        time_str, package_id = user_input.split(" ")
    elif state == "r":
        print("To go back, enter 'b'")
        user_input = input()
        if user_input == "b":
            state = ""
            continue
    elif state == "t":
        print(
            "Enter the truck id, followed by an 'r' to view routes, or a'd' to view total distance. Enter 'b' to go back."
        )
        print("Example viewing the total distance for truck 2:\n\t2 d")
        user_input = input()
        if user_input == "b":
            state = ""
            continue
    else:
        print(
            "Enter 'p' to track a package, 'r' to view routes, or 't' to view truck information. Enter 'q' to quit."
        )
        user_input = input()
        if user_input in ["p", "r", "t", "q"]:
            state = user_input
        else:
            "Invalid option."
