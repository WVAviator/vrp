from typing import Optional

from utilities.time import time_str_to_int


class Package:
    def __init__(
        self,
        package_id: int,
        address: str,
        deadline: str,
        city: str,
        zip_code: str,
        weight: int,
        note: str,
    ):
        self.package_id = package_id
        self.address = address
        self.deadline = deadline
        self.city = city
        self.zip_code = zip_code
        self.weight = weight
        self.note = note
        self.constraints = PackageConstraints(deadline, note)
        self.status = (
            "delayed" if self.constraints.delayed_until > 480 else "at the hub"
        )
        self.tracking_info: list[tuple[float, str]] = []
        self.group_id = package_id

        # Set initial tracking info
        if self.constraints.delayed_until > 480 and self.constraints.updated_address:
            self.add_tracking_info(480, "On hold: Invalid address")
        elif self.constraints.delayed_until > 480:
            self.add_tracking_info(480, "Delayed inbound to the hub")
        else:
            self.add_tracking_info(480, "Ready for delivery at the hub")

    def formatted_address(self):
        """
        Returns the address formatted with zip code to be used in distance table lookups.
        """
        return self.address + " " + self.zip_code

    def add_tracking_info(self, time: float, message: str):
        """
        Appends a message to the package's tracking info.
        """
        time_str = f"{int(time // 60)}:{int(time % 60):02d}"
        self.tracking_info.append((time, f"{time_str} - {message}"))

    def get_tracking_info(self, time: float) -> list[str]:
        """
        Given a time, return all tracking info before that time.
        """
        return [t[1] for t in self.tracking_info if t[0] <= time]

    def __repr__(self):
        return f"{{ id: {self.package_id}, address: {self.address}, deadline: {self.deadline}, status: {self.status} }}"


class PackageConstraints:
    def __init__(self, deadline: str, note: str):
        self.deadline = time_str_to_int(deadline)
        self.delayed_until = 480
        self.updated_address = ""
        self.updated_zip_code = ""
        self.required_truck = None
        self.paired_packages = []

        # This parses the package info and notes into usable logic and restrictions for measuring package constraints
        if note.startswith("Delayed on flight"):
            words = note.split(" ")
            delay_time = " ".join(words[-2:])
            self.delayed_until = time_str_to_int(delay_time)
        elif note.startswith("Wrong address"):
            self.delayed_until = time_str_to_int("10:20 AM")

            # Hardcoding the updated address since it's not included in the input materials
            # In a production implementation, this information will be able to be added once it becomes available
            self.updated_address = "410 S State St"
            self.updated_zip_code = "84111"
        elif note.startswith("Can only be on truck"):
            self.required_truck = int(note.split(" ")[-1])
        elif note.startswith("Must be delivered with"):
            listed_packages = note.split("Must be delivered with ")
            package_ids = listed_packages[-1].split(", ")
            self.paired_packages = [int(package_id) for package_id in package_ids]
