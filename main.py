from wgups.distance_table import DistanceTable
from wgups.package_table import PackageTable
from wgups.savings_list import SavingsList


pt = PackageTable("resources/WGUPS Package File.csv")
dt = DistanceTable("resources/WGUPS Distance Table.csv")


savings_list = SavingsList(pt, dt)
print(savings_list)

for _, p1, p2 in savings_list:
    pass
