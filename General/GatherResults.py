# -*- coding: cp1252 -*-
import dbf

import geopandas as gpd
import pandas as pd
from math import floor

import glob



files = glob.glob("D:/EK/1/outputs/data/demand/B*.csv")
fl�chen = pd.read_csv("D:/EK/1/outputs/data/demand/Total_demand.csv", sep= ",", decimal= ".")

losses = ["Qhs_sys_kWh"]

for i, buildingName in enumerate(files):
    building = pd.read_csv(buildingName, sep= ",", decimal= ".")
    HWB = building["Qhs_sys_kWh"].sum() / fl�chen["GFA_m2"][i]
    #print(f"HWB: {HWB}")
    KWB = (building["Qcs_lat_sys_kWh"].sum() + building["Qcs_sen_sys_kWh"].sum()) / fl�chen["GFA_m2"][i]
    print(f"KWB: {KWB}")










