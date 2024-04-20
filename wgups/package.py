from typing import Optional


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
        self.tracking_info = []
        self.group_id = package_id

    def formatted_address(self):
        return self.address + " " + self.zip_code

    def add_tracking_info(self, time: float, message: str):
        time_str = f"{int(time // 60)}:{int(time % 60):02d}"
        self.tracking_info.append(f"{time_str} - {message}")

    def __repr__(self):
        return f"{{ id: {self.package_id}, address: {self.address}, deadline: {self.deadline}, status: {self.status} }}"


def time_str_to_int(time_str: str) -> int:
    if time_str == "EOD":
        return 1440
    time, period = time_str.split(" ")
    hours_str, minutes_str = time.split(":")
    hours = int(hours_str)
    minutes = int(minutes_str)
    if period.upper() == "PM":
        hours += 12
    return hours * 60 + minutes


class PackageConstraints:
    def __init__(self, deadline: str, note: str):
        self.deadline = time_str_to_int(deadline)
        self.delayed_until = 480
        self.updated_address = ""
        self.updated_zip_code = ""
        self.required_truck = None
        self.paired_packages = []

        if note.startswith("Delayed on flight"):
            words = note.split(" ")
            delay_time = " ".join(words[-2:])
            self.delayed_until = time_str_to_int(delay_time)
        elif note.startswith("Wrong address"):
            self.delayed_until = time_str_to_int("10:20 AM")

            # Hardcoding the updated address since it's not included in the input materials
            self.updated_address = "410 S State St"
            self.updated_zip_code = "84111"
        elif note.startswith("Can only be on truck"):
            self.required_truck = int(note.split(" ")[-1])
        elif note.startswith("Must be delivered with"):
            listed_packages = note.split("Must be delivered with ")
            package_ids = listed_packages[-1].split(", ")
            self.paired_packages = [int(package_id) for package_id in package_ids]
