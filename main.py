from typing import List

class Address:
    def __init__(self, street: str, city: str, state: str, zip: str) -> None:
        self.street = street
        self.city = city
        self.state = state
        self.zip = zip

    def __hash__(self) -> int:
        return hash(self.street + self.city + self.state + self.zip)

class SpecialNote:
    def __init__(self, required_trucks: list[str], delayed: int, address_update: Address, paired_packages: list[str]) -> None:
        self.required_trucks = required_trucks
        self.delayed = delayed
        self.address_update = address_update
        self.paired_packages = paired_packages

class Package:
    def __init__(self, id: str, address: Address, deadline: int, weight: int, special_note: SpecialNote) -> None:
        self.id = id
        self.address = address
        self.deadline = deadline
        self.weight = weight
        self.special_note = special_note
        
class Truck:
    def __init__(self, id: str) -> None:
        self.id = id

def calculate_savings(dist_matrix: list[list[float]], i, j) -> int:
    if i > j:
        i, j = j, i
    cost_separate = 2 * dist_matrix[i][0] + 2 * dist_matrix[j][0]
    cost_together = dist_matrix[i][0] + dist_matrix[j][i] + dist_matrix[j][0]
    savings = cost_separate - cost_together
    return savings

def get_savings_list(matrix: list[list[float]]) -> list[tuple[float, int, int]]:
    savings_list = []
    for i in range(0, len(matrix)):
        for j in range(i + 1, len(matrix[i])):
            savings_list.append((calculate_savings(matrix, i, j), i, j))

    savings_list.sort(reverse=True)

    return savings_list

matrix = [[0.0, 0, 0, 0, 0], [6, 0, 0, 0, 0], [4, 10, 0, 0, 0], [3, 9, 1, 0, 0], [8, 4, 12, 11, 0]]
savings_list = get_savings_list(matrix)

print(savings_list)
        
trucks = 2

delivered = set()
packages = [4, 4, 1, 3, 4, 2]

class Route:
    def __init__(self, packages: list[int]):
        self.route = [0] + packages + [0]

    def contains_external(self, package: int) -> bool:
        """
        Verifies whether the provided package id is both part of this route and external (adjacent to the hub)
        """
        return self.route[1] == package or self.route[-2] == package

    def insert(self, package: int, adjacent_package: int):
        """
        Given a package id and adjacent package id that is external, inserts the package on the appropriate end of the route.
        """
        if self.route[-2] == adjacent_package:
            self.route.insert(-1, package)
        else:
            self.route.insert(1, package)

    def remove(self, package: int):
        """
        Removes the provided package from the route if it is external. Useful for backtracking.
        """
        if self.route[1] == package or self.route[-2] == package:
            self.route.remove(package)

    def merge(self, route: 'Route', i: int, j: int):
        """
        Merges route with another route given the two external nodes i and j.
        """

        if i > j:
            i, j = j, i

        if self.route[-2] == i and route.route[1] == j:
            self.route = self.route[:-1] + route.route[1:]
        elif self.route[1] == i and route.route[-2] == j:
            self.route = route.route[:-1] + self.route[1:]
        elif self.route[1] == i and route.route[1] == j:
            self.route = route.route[::-1][1:] + self.route[1:]
        elif self.route[-2] == i and route.route[-2] == j:
            self.route = self.route[:-1] + route.route[::-1][1:]

    def split(self, i: int, j: int) -> 'Route':
        """
        Splits the route into two routes given the two external nodes i and j. Useful for backtracking.
        """

        index_i = self.route.index(i)
        index_j = self.route.index(j)

        split_index = max(index_i, index_j)

        other = Route(self.route[split_index:-1])
        self.route = self.route[:split_index] + [0]
        return other


        

for truck in range(trucks):
    loaded = set()
    routes = []
    for (_, i, j) in savings_list:
        if i not in loaded and j not in loaded:
            if i in delivered or j in delivered:
                continue
            new_route = [0, i, j, 0]
            routes.append(new_route)
        elif i in loaded and j not in loaded:
            if j in delivered:
                continue
            for route in routes:
                if route[1] == i:
                    route.insert(1, j)
                    break
                elif route[-2] == i:
                    route.insert(-1, j)
                    break
        elif j in loaded and i not in loaded:
            if i in delivered:
                continue
            for route in routes:
                if route[1] == j:
                    route.insert(1, i)
                    break
                elif route[-2] == j:
                    route.insert(-2, i)
                    break
        elif j in loaded and i in loaded:


                


