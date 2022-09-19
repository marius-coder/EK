# -*- coding: cp1252 -*-

import shutil
def ResetSupply():
    for i,year in enumerate(["2024","2027","2030","2040","2050"]):
            for prio in ["Prio Fernw�rme","Prio W�rmepumpe"]:
                #print(f"Szenarienjahr: {year} mit prio: {prio}")
                path= f'./Scenarios/{year}/{prio}'
                shutil.copy2(f"C:/Users/cermak/source/repos/EK/General/Scenarios/2020/Prio Fernw�rme/supply_systems.dbf", f"{path}/supply_systems.dbf")
ResetSupply()