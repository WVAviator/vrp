from wgups.package_table import PackageTable


def test_package_table():
    package_table = PackageTable("resources/WGUPS Package File.csv")
    package1 = package_table.get_package(1)
    package40 = package_table.get_package(40)

    if package1 is None or package40 is None:
        assert False

    assert package1.package_id == 1
    assert package1.address == "195 W Oakland Ave"
    assert package1.weight == 21
    assert package1.status == "at the hub"

    assert package40.package_id == 40
    assert package40.address == "380 W 2880 S"
    assert package40.weight == 45
    assert package40.status == "at the hub"


def test_package_constraints():
    package_table = PackageTable("resources/WGUPS Package File.csv")

    package3 = package_table.get_package(3)
    assert package3 != None
    assert package3.constraints.required_truck == 2
    assert package3.constraints.deadline == 1440

    package9 = package_table.get_package(9)
    assert package9 != None
    assert package9.constraints.delayed_until == 620
    assert package9.constraints.updated_address == "410 S State St"

    package20 = package_table.get_package(20)
    assert package20 != None
    assert package20.constraints.paired_packages == [13, 15]
    assert package20.constraints.deadline == 630
