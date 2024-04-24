# Alexander Durham - Student ID 011565339

from utilities.time import time_float_to_str
from wgups.solution_factory import SolutionFactory


# Uses the solution factory to heuristically generate multiple solutions and return the best one.
solution_factory = SolutionFactory()
best_solution = solution_factory.generate_best_solution()

if best_solution == None:
    print("No solution found. Exiting...")
    exit()

print("\n\n\n==== Best Solution ====\n")
print(best_solution)
print("\n")

# REPL start
state = ""
while state != "q":
    # Package tracking view state
    if state == "p":
        print(
            "To track a package, enter the package ID (or 'all') followed (optionally) by the time (00:00-24:00) separated by a space. Enter 'b' to go back."
        )
        user_input = input()
        if user_input == "b":
            state = ""
            continue

        # if no space exists in the string, only a package ID was provided
        if not " " in user_input:
            time_str = "24:00"
            package_id = user_input
        else:
            package_id, time_str = user_input.split(" ")

        if not ":" in time_str:
            print("Invalid time string. Examples: 9:25, 11:15, 14:48\n")

        hour_str, minute_str = time_str.split(":")
        if not hour_str.isnumeric or not minute_str.isnumeric:
            print("Invalid time string. Examples: 9:25, 11:15, 14:48\n")

        h, m = int(hour_str), int(minute_str)
        time = h * 60 + m

        if package_id == "all":
            packages = best_solution.get_package_list()

            if time == 1440:
                print("==== Package Statuses - EOD ====\n")
            else:
                print(f"==== Package Statuses - {time_float_to_str(time)} ====\n")

            for package in packages:
                info = package.get_tracking_info(time)

                time_str, message = info[-1].split(" - ")
                if (
                    message.split(" ")[0] == "Delivered"
                    or message.split(" ")[0] == "Departed"
                ):
                    latest_update = f"{message} at {time_str}"
                else:
                    latest_update = f"{message}"

                print(f"Package {package.package_id}: {latest_update}")

            print("\n===========================\n")
            continue

        if not package_id.isnumeric():
            print("Invalid package ID\n")
        package_id = int(package_id)

        if not best_solution.print_package_info(package_id, time):
            print("Package ID not found.\n")

    # Route information view state
    elif state == "r":
        print("==== Route Information ====\n")
        best_solution.print_routes()
        print("===========================\n")
        state = ""

    # Truck information view state
    elif state == "t":
        print(
            "Enter the truck id to view distance and route info. Enter 'b' to go back."
        )
        user_input = input()
        if user_input == "b":
            state = ""
            continue
        if not user_input.isnumeric():
            print("Invalid truck id.\n")
            continue
        truck_id = int(user_input)
        if not best_solution.print_truck_info(truck_id):
            print("Invalid truck id.\n")

    # Main view state
    else:
        print(
            "Enter 'p' to track a package, 'r' to view routes, or 't' to view truck information. Enter 'q' to quit."
        )
        user_input = input()
        if user_input in ["p", "r", "t", "q"]:
            state = user_input
        else:
            "Invalid option."
