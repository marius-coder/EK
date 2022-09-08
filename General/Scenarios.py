# -*- coding: cp1252 -*-

import pandas as pd



def SetupInput(year:int):
    SetupTypology()
    SetupArchitecture()
    SetupInternalLoads()
    SetupIndoorComfort()
    SetupAirConditioning()
    SetupSupplySystems()
    SetupSurroundings()
    SetupShedules()





for scen in ["WP","FW"]:
    for year in [2020,2024,2027,2030]:
        SetupInput(year) #Saniert Gebäude







