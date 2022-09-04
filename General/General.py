# -*- coding: cp1252 -*-
import dbf

import geopandas as gpd
import pandas as pd
from math import floor

datenGenerell = pd.read_csv("Daten.csv", sep= ";")
#print(datenGenerell.info())

datenBuildings = pd.read_csv("Quartiersdaten.csv", sep= ";")
#print(datenBuildings.info())

data = gpd.read_file("zone.shp")
#print(data["geometry"].area)

Sanierungszyklus = 40 #Jahre

timelines= {
    "1960-1976" : [1960,1976],
    "1976-1993" : [1976,1993],
    "1993-2001" : [1993,2001],
    "2001+"     : [2001,9999]    
    }

baujahre= {
    "Gründerzeit" : 1873,
    "Wiederaufbau (1945-1960)" : 1945,
    "Wirtschaftswunder (1961-1980)" : 1961,
    "Gemischt (1961-1980)" : 1981    
    }

WW = {
    "Innenhof" : 5,
    "Wohnen" : 40,
    "Restaurant" : 60,
    "Gewerbe" : 15,
    "EG Restaurant" : 60,
    "EG Gewerbe" : 15
    }

def CalcWWVerbrauch(area, buildingPersonen, typ, floors):
    #print(typ)
    if "EG" in typ:
        persProStock = buildingPersonen / floors
        return (WW[typ] * persProStock + WW["Wohnen"] * persProStock * (floors-1)) / buildingPersonen
    elif typ == "Innenhof":
        #print("INNENHOF")
        return WW[typ]
    else:
        return WW[typ]

EPRO_WM2 = 10
QCRE_WM2 = 15
ED_WM2 = 5

def GetCoolingDemand(area, floors, typ):    
    if "EG" in typ:
        areaGewerbe = area / floors
        demand_QCRE_WM2 = (areaGewerbe * QCRE_WM2 + 0 * floors) / (floors * area)
        demand_ED_WM2 = (areaGewerbe * ED_WM2 + 0 * floors) / (floors * area)
        demand_EPRO_WM2 = (areaGewerbe * EPRO_WM2 + 0 * floors) / (floors * area)
        return demand_QCRE_WM2, demand_ED_WM2, demand_EPRO_WM2
    elif typ == "Gewerbe" or typ == "Restaurant":
        return QCRE_WM2, ED_WM2, EPRO_WM2
    else:
        return 0,0,0


def EditInternalLoads(dic_Buildings:dict, quartier:int, i:int):
    personen= datenGenerell["Einwohnerdichte"][quartier-1]
    with dbf.Table('internal_loads.dbf') as table:
        table.open(dbf.READ_WRITE) #open dbf file with write privileges
        
        for key,val in dic_Buildings.items():
            buildingPersonen =(val * 100 * personen)/sum([i*100 for i in dic_Buildings.values()])
            area = data["geometry"][key].area  * data["floors_ag"][key]
            index = datenBuildings[datenBuildings['Gebäude'] == f'B{str(key+1).zfill(3)}'].index
            areaPerPerson = area / buildingPersonen
            floors = data["floors_ag"][key]
            area = data["geometry"][key].area
            typ = datenBuildings["Art Nutzung"][index[0]]
            wwVerbrauch = CalcWWVerbrauch(area= area, buildingPersonen= buildingPersonen, typ= typ, floors= floors)
            #print(wwVerbrauch)
            i += 1
            with table[key] as rec:
                rec.OCC_M2P = areaPerPerson
                rec.VWW_LDP = wwVerbrauch
                rec.VW_LDP = wwVerbrauch * 4                
                rec.QCRE_WM2 = GetCoolingDemand(area= area, floors= floors, typ= typ)[0]
                rec.ED_WM2 = GetCoolingDemand(area= area, floors= floors, typ= typ)[1]
                rec.EPRO_WM2 = GetCoolingDemand(area= area, floors= floors, typ= typ)[2]

def EditSupplySystems(dic_Buildings:dict, quartier:int, i:int):
    with dbf.Table('supply_systems.dbf') as table:
        table.open(dbf.READ_WRITE) #open dbf file with write privileges
        for key,val in dic_Buildings.items():
            index = datenBuildings[datenBuildings['Gebäude'] == f'B{str(key+1).zfill(3)}'].index
            if datenBuildings["Kühlung"][index[0]] == "Ja":
                with table[key] as rec:
                    rec.TYPE_CS = "SUPPLY_COOLING_AS1"

def EditAirConditioning(dic_Buildings:dict, quartier:int, i:int):
    with dbf.Table('air_conditioning.dbf') as table:
        table.open(dbf.READ_WRITE) #open dbf file with write privileges
        for key,val in dic_Buildings.items():
            index = datenBuildings[datenBuildings['Gebäude'] == f'B{str(key+1).zfill(3)}'].index
            if datenBuildings["Lüftung"][index[0]] == "Ja":
                with table[key] as rec:
                    rec.TYPE_VENT = "HVAC_VENTILATION_AS1"
            if datenBuildings["Kühlung"][index[0]] == "Ja":
                with table[key] as rec:
                    rec.TYPE_CS = "HVAC_COOLING_AS3"


def GetTypology()->dict:
    with dbf.Table('typology.dbf') as table:

        for quartier in range(1,27):

            dic_Buildings = {}

            for i, building in enumerate(datenBuildings[datenBuildings["Quartier"]== quartier]["Gebäude"]):
                index= int(building[1:])-1

                for use,percent in zip(["1ST_USE","2ND_USE","3RD_USE"],["1ST_USE_R","2ND_USE_R","3RD_USE_R"]):

                    #print(table[index])
                    #print(getattr(table[index],use))
                    if getattr(table[index],use).replace(" ","") == "MULTI_RES":
                        dic_Buildings[index] = getattr(table[index],percent)

            
            EditInternalLoads(dic_Buildings= dic_Buildings, quartier= quartier, i=i)
            EditSupplySystems(dic_Buildings= dic_Buildings, quartier= quartier, i=i)
            EditAirConditioning(dic_Buildings= dic_Buildings, quartier= quartier, i=i)

def CalcSanierung(quartier:int) -> int:
    baujahr = baujahre[datenGenerell["Bauzeit"][quartier-1]]
    sanJahr = baujahr + floor((2022-baujahr)/Sanierungszyklus) * Sanierungszyklus
    return sanJahr

def GetQuartiersNummer(building:str)->int:
    return int(datenBuildings.loc[datenBuildings['Gebäude'] == building]["Quartier"])

def GetTimeline(sanJahr:int) -> str:
    for key,val in timelines.items():
        if sanJahr in range(val[0],val[1]):
            return key

def GetValue(building:str) -> str:
    quartier= GetQuartiersNummer(building= building)

    sanJahr= CalcSanierung(quartier)    
    sanQual = GetTimeline(sanJahr)   
    return sanQual

GetTypology()

with dbf.Table('architecture.dbf') as table:
    table.open(dbf.READ_WRITE) #open dbf file with write privileges
    for i,record in enumerate(dbf.Process(table)): #iterate entries
        #print(f"Building: {record.NAME}")
        sanQual = GetValue(building= record.name.replace(" ",""))

        record.TYPE_FLOOR = "FLOOR_"+sanQual
        record.TYPE_PART = "WALL_"+sanQual
        record.TYPE_BASE = "FLOOR_"+sanQual
        record.TYPE_ROOF = "ROOF_"+sanQual
        record.TYPE_WALL = "WALL_"+sanQual
        record.TYPE_WIN = "WINDOW_"+sanQual

