from wgups.package_table import PackageTable

def test_package_table():
    package_table = PackageTable("resources/WGUPS Package File.xlsx")
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
