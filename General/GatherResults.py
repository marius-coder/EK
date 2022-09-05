# -*- coding: cp1252 -*-
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import glob

if 1:
    files = glob.glob("C:/Users/cermak/Documents/EK/1/outputs/data/demand/B*.csv")
    fl�chen = pd.read_csv("C:/Users/cermak/Documents/EK/1/outputs/data/demand/Total_demand.csv", sep= ",", decimal= ".")

    losses = ["Qhs_sys_kWh"]

    HWB = []
    Heizlast = []
    for i, buildingName in enumerate(files):
        
        #W�rmeseite
        building = pd.read_csv(buildingName, sep= ",", decimal= ".")
        HWB.append(building["Qhs_sys_kWh"].sum() / fl�chen["GFA_m2"][i])
        
        if building["Qhs_sys_kWh"].sum() / fl�chen["GFA_m2"][i] > 150: print(i)
            
        Heizlast.append(building["Qhs_sys_kWh"].max() / fl�chen["GFA_m2"][i] * 1000)

        #K�lteseite
        KWB = (building["Qcs_lat_sys_kWh"].sum() + building["Qcs_sen_sys_kWh"].sum()) / fl�chen["GFA_m2"][i]
        K�hllast = building[['Qcs_lat_sys_kWh', 'Qcs_sen_sys_kWh']].sum(1).max()
        #print(K�hllast)

        #Stromseite
        stromBedarf = building["E_sys_kWh"].sum() / fl�chen["GFA_m2"][i]
        maxLeistung = building["E_sys_kWh"].max()
        #print(maxLeistung)

    data = pd.DataFrame()
    data["HWB"] = HWB
    data["Heizlast"] = Heizlast
    data["KWB"] = KWB
    data["K�hllast"] = K�hllast
    data["Strombedarf"] = stromBedarf
    data["maxLeistung"] = maxLeistung
    data.to_csv("Ergebnis.csv")
    

data = pd.read_csv("Ergebnis.csv")
data["Baujahr"] =  pd.read_csv("Baujahre.csv")["0"]

sns.histplot(data= data["HWB"], bins= 100)
plt.show()

sns.scatterplot(x=data["Baujahr"], y= data["HWB"])
plt.show()

