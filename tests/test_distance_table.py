from wgups.distance_table import DistanceTable
from wgups.package_table import PackageTable


def test_basic_import():
    p_table = PackageTable("resources/WGUPS Package File.csv")
    d_table = DistanceTable("resources/WGUPS Distance Table.csv", p_table)

    assert d_table.get_distance("1060 Dalton Ave S 84104", "HUB") == 7.2
    assert (
        d_table.get_distance("6351 South 900 East 84121", "600 E 900 South 84105")
        == 8.3
    )


def test_all_addresses_correct():
    p_table = PackageTable("resources/WGUPS Package File.csv")
    d_table = DistanceTable("resources/WGUPS Distance Table.csv", p_table)

    for i in range(1, 41):
        package = p_table.get_package(i)
        if package == None:
            assert False
        package_addr = package.formatted_address()
        d_table.get_distance("HUB", package_addr)

    assert True
