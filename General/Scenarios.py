# -*- coding: cp1252 -*-

import pandas as pd
import random
random.seed(10)
from General import *

import shutil

def GetBuildingsWithGas(data):
    buildingsWithGas = []

    for index in range(len(data)):
        if data["heizart"] == "Gas":
            buildingsWithGas.append(index)
    return buildingsWithGas

percents = {
    "2020" : 0.33333333333,
    "2024" : 0.66666666666,
    "2027" : 1,
    "2030" : 1,
    "2040" : 1,
    "2050" : 1,
    }

prioValues = {
    "Prio Fernwärme" : 25,
    "Prio Wärmepumpe" : 35,
    }


def GetLastResults(prio, i):
    import random
    random.seed(10)
    buildingsToChangeInter = []
    buildingsToChange = []
    year = ["2020","2024","2027","2030","2040","2050"][i-1]
    #print(f"Bezugsjahr: {year}")
    path= f'./Scenarios/{year}/{prio}'
    #print(f"Pfad vom alten Supply: {path}")
    with dbf.Table(f"./Scenarios/2020/{prio}/supply_systems.dbf") as table: #Alten Supply öffnen
        table.open(dbf.READ_WRITE) #open dbf file with write privileges
        for index,record in enumerate(dbf.Process(table)):
            #print(record.TYPE_HS)
            if record.TYPE_HS.replace(" ","") == "SUPPLY_HEATING_AS3": 
                buildingsToChangeInter.append(f'B{str(index+1).zfill(3)}')
    #print(f"Gebäude mit Gas:{len(buildingsToChangeInter)}")
    if year == "2030":
        print("")
    for _ in range(int(127*percents[year])):
        choice = random.choice(buildingsToChangeInter)
        buildingsToChangeInter.remove(choice)
        buildingsToChange.append(choice)
    #print(f"Gebäude die geändert werden:{len(buildingsToChange)}")
    #for index in range(178):
        #buildingID = f'B{str(index+1).zfill(3)}'
       # EditSupplySystems(buildingID= buildingID,path= f"{path}/")
    year = ["2020","2024","2027","2030","2040","2050"][i]
    path= f'./Scenarios/{year}/{prio}'
    if year in ["2020","2024","2027","2030"]:
        for buildingID in buildingsToChange:
            RenewSupplySystem(buildingID= buildingID, path= path, prio= prio)


def RenewSupplySystem(buildingID, path, prio):
    #print(f"Pfad zum editieren: {path}")
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

def RunScen():
    for i,year in enumerate(["2020","2024","2027","2030","2040","2050"]):
        for prio in ["Prio Fernwärme","Prio Wärmepumpe"]:
            #print(f"Szenarienjahr: {year} mit prio: {prio}")
            for index in range(178):
                buildingID = f'B{str(index+1).zfill(3)}'
                path= f'./Scenarios/{year}/{prio}'
                EditInternalLoads(buildingID= buildingID,path= f"{path}/")
            if year != "2020": GetLastResults(prio= prio, i= i)
        
            if year == "2020":
                EditArchitecture(currentYear= int(year), path= f"./Scenarios/{year}/")
            else:
                EditArchitecture(currentYear= int(year), path= f"./Scenarios/{year}/{prio}/")
def ResetSupply():
    for i,year in enumerate(["2024","2027","2030","2040","2050"]):
            for prio in ["Prio Fernwärme","Prio Wärmepumpe"]:
                #print(f"Szenarienjahr: {year} mit prio: {prio}")
                path= f'./Scenarios/{year}/{prio}'
                shutil.copy2(f"C:/Users/mariu/source/repos/General/General/Scenarios/2020/Prio Fernwärme/supply_systems.dbf", f"{path}/supply_systems.dbf")
ResetSupply()
RunScen()


