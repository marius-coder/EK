# -*- coding: cp1252 -*-

import pandas as pd
import random
random.seed(10)
from General import *


def GetBuildingsWithGas(data):
    buildingsWithGas = []

    for index in range(len(data)):
        if data["heizart"] == "Gas":
            buildingsWithGas.append(index)
    return buildingsWithGas

percents = {
    "2020" : 0,
    "2024" : 0.33333333333,
    "2027" : 0.66666666666,
    "2030" : 1,
    "2040" : 1,
    "2050" : 1,
    }

prioValues = {
    "Prio Fernwärme" : 25,
    "Prio Wärmepumpe" : 35,
    }


def GetLastResults(prio, i):
    buildingsToChange = []
    year = ["2020","2024","2027","2030","2040","2050"][i-1]
    print(f"Bezugsjahr: {year}")
    path= f'./Scenarios/{year}/{prio}'
    print(f"Pfad vom alten Supply: {path}")
    with dbf.Table(f"{path}/supply_systems.dbf") as table: #Alten Supply öffnen
        table.open(dbf.READ_WRITE) #open dbf file with write privileges
        
        for index,record in enumerate(dbf.Process(table)):
            #print(record.TYPE_HS)
            if record.TYPE_HS.replace(" ","") == "SUPPLY_HEATING_AS3": 
                buildingsToChange.append(f'B{str(index+1).zfill(3)}')
    buildingsToChange = random.choices(buildingsToChange, k=int(len(buildingsToChange)*percents[year]))
    #print(len(buildingsToChange))
    year = ["2020","2024","2027","2030","2040","2050"][i]
    path= f'./Scenarios/{year}/{prio}'
    for buildingID in buildingsToChange:
        RenewSupplySystem(buildingID= buildingID, path= path, prio= prio)


def RenewSupplySystem(buildingID, path, prio):
    print(f"Pfad zum editieren: {path}")
    data = pd.read_csv(f"{path}/Ergebnis/Ergebnis.csv")
    with dbf.Table(f"{path}/supply_systems.dbf") as table:
        table.open(dbf.READ_WRITE) #open dbf file with write privileges
        index= int(buildingID[1:])-1
        with table[index] as rec:
            if data["Heizlast"][index] > prioValues[prio]:            
                rec.TYPE_DHW = "SUPPLY_HOTWATER_AS9"
                rec.TYPE_HS = "SUPPLY_HEATING_AS9"
            else:
                rec.TYPE_DHW = "SUPPLY_HOTWATER_AS7"
                rec.TYPE_HS = "SUPPLY_HEATING_AS7"

for i,year in enumerate(["2020","2024","2027","2030","2040","2050"]):
    print(f"Szenarienjahr: {year}")
    for prio in ["Prio Fernwärme","Prio Wärmepumpe"]:
        if year != "2020": GetLastResults(prio= prio, i= i)
        
        if year == "2020":
            EditArchitecture(currentYear= int(year), path= f"./Scenarios/{year}/")
        else:
            EditArchitecture(currentYear= int(year), path= f"./Scenarios/{year}/{prio}/")




