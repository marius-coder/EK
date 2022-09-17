# -*- coding: cp1252 -*-
import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt
import glob
import dbf


zuhause = "C:/Users/mariu/EK/1/outputs/data/demand/"
arbeit = "C:/Users/cermak/Documents/EK/1/outputs/data/demand/"

if 1:
    files = glob.glob(f"{arbeit}B*.csv")
    fl�chen = pd.read_csv(f"{arbeit}Total_demand.csv", sep= ",", decimal= ".")
    data = gpd.read_file("zone.shp")
    HWB = []
    Heizlast = []
    heizart = []
    stromBedarf = []
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
        stromBedarf.append(building["E_sys_kWh"].sum() / fl�chen["GFA_m2"][index])
        maxLeistung.append(building["E_sys_kWh"].max())
        #print(maxLeistung)

        with dbf.Table('supply_systems.dbf') as table:
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
    data.to_csv("Ergebnis.csv")
    

data = pd.read_csv("Ergebnis.csv")
data["Baujahr"] =  pd.read_csv("Baujahre.csv")["0"]

sns.histplot(data= data["Heizlast"], bins= 100)
#plt.show()

sns.scatterplot(x=data["Baujahr"], y= data["Heizlast"])
#plt.show()

