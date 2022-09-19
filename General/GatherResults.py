# -*- coding: cp1252 -*-
import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt
import glob
import dbf
import shutil

from Scenarios import RunScen, ResetSupply
zuhause = "C:/Users/mariu/EK/1/outputs/data/demand/"
arbeit = "C:/Users/cermak/Documents/EK/1/outputs/data/demand/"

def Run(path):
    files = glob.glob(f"{arbeit}B*.csv")
    fl�chen = pd.read_csv(f"{arbeit}Total_demand.csv", sep= ",", decimal= ".")
    data = gpd.read_file("zone.shp")
    HWB = []
    Heizlast = []
    heizart = []
    stromBedarf = []
    stromBedarfHeizen = []
    maxLeistung = []
    KWB = []
    K�hllast = []
    fl�che = []
    for index, buildingName in enumerate(files):
        fl�che.append(data["geometry"][index].area * data["floors_ag"][index])
        #W�rmeseite
        building = pd.read_csv(buildingName, sep= ",", decimal= ".")
        HWB.append(building["Qhs_sys_kWh"].sum() / fl�chen["GFA_m2"][index])
        
        #if building["Qhs_sys_kWh"].sum() / fl�chen["GFA_m2"][index] > 150: print(index)
            
        Heizlast.append(building["Qhs_sys_kWh"].max() / fl�chen["GFA_m2"][index] * 1000)

        #K�lteseite
        KWB.append((building["Qcs_lat_sys_kWh"].sum() + building["Qcs_sen_sys_kWh"].sum()) / fl�chen["GFA_m2"][index])
        K�hllast.append(building[['Qcs_lat_sys_kWh', 'Qcs_sen_sys_kWh']].sum(1).max())
        #print(K�hllast)
        
        #Stromseite
        #print(f'Fl�che: {fl�chen["GFA_m2"][index]}')
        #print(f'Strombedarf: {building["E_sys_kWh"].sum()}')
        stromBedarf.append((building["E_sys_kWh"].sum() + building["E_ww_kWh"].sum() + building["E_hs_kWh"].sum() + building["Eve_kWh"].sum() + building["E_cs_kWh"].sum()) / fl�chen["GFA_m2"][index])
        stromBedarfHeizen.append(building["Eaux_kWh"].sum() / fl�chen["GFA_m2"][index])
        maxLeistung.append(building["E_sys_kWh"].max())
        #print(maxLeistung)

        with dbf.Table(f'{path}supply_systems.dbf') as table:
            table.open(dbf.READ_WRITE) #open dbf file with write privileges
            with table[index] as rec:
                if rec.TYPE_HS.replace(" ","") == "SUPPLY_HEATING_AS3":
                    heizart.append("Gas")
                elif rec.TYPE_HS.replace(" ","") == "SUPPLY_HEATING_AS9":
                    heizart.append("Fernw�rme")
                elif rec.TYPE_HS.replace(" ","") == "SUPPLY_HEATING_AS7":
                    heizart.append("W�rmepumpe")
                else:
                    heizart.append("Unbekannt")
    data = pd.DataFrame()
    data["HWB"] = HWB
    data["Heizlast"] = Heizlast
    data["KWB"] = KWB
    data["K�hllast"] = K�hllast
    data["Strombedarf"] = stromBedarf
    data["maxLeistung"] = maxLeistung
    data["heizart"] = heizart
    data["Fl�che"] = fl�che
    data["Strombedarfheizen"] = stromBedarfHeizen
    data.to_csv(f"{path}/Ergebnis/Ergebnis.csv")

for i,year in enumerate(["2020","2024","2027","2030","2040","2050"]):
    ResetSupply()
    RunScen()
    f = 0
    for prio in ["Prio Fernw�rme","Prio W�rmepumpe"]:

        print(f"Szenarienjahr: {year} mit prio: {prio}")
        path = f"C:/Users/cermak/source/repos/EK/General/Scenarios/{year}/{prio}/"
        shutil.copy2(f"{path}/air_conditioning.dbf", "C:/Users/cermak/Documents/EK/1/inputs/building-properties/air_conditioning.dbf")
        shutil.copy2(f"{path}/architecture.dbf", "C:/Users/cermak/Documents/EK/1/inputs/building-properties/architecture.dbf")
        shutil.copy2(f"{path}/supply_systems.dbf", "C:/Users/cermak/Documents/EK/1/inputs/building-properties/supply_systems.dbf")
        shutil.copy2(f"{path}/typology.dbf", "C:/Users/cermak/Documents/EK/1/inputs/building-properties/typology.dbf")
        shutil.copy2(f"{path}/internal_loads.dbf", "C:/Users/cermak/Documents/EK/1/inputs/building-properties/internal_loads.dbf")
        print(f"In CEA sollte {f+1} stehen")
        input("Press Enter to continue...")
        print(f"Gathering Results from {path}")
        Run(path)