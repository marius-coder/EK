# -*- coding: cp1252 -*-
import dbf

import geopandas as gpd
import pandas as pd
from math import floor
import random

random.seed(10)

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
    "2001-2019" : [2001,2019],
    "2019-2030" : [2019,2030],
    "2030+"     : [2030,9999]    

    }

baujahre= {
    "Gründerzeit" : [1873,1944],
    "Wiederaufbau (1945-1960)" : [1945,1960],
    "Wirtschaftswunder (1961-1980)" : [1961,1980],
    "Gemischt (1961-1980)" : [1981,1990]
    }

WW = {
    "Innenhof" : 5,
    "Wohnen" : 40,
    "Restaurant" : 60,
    "Gewerbe" : 15,
    "EG Restaurant" : 60,
    "EG Gewerbe" : 15
    }

PersProm2 = 7

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


def EditInternalLoads(buildingID, path= ""):


    dic_Buildings, quartier = GetQuartierInfo(buildingID= buildingID)
    personen= datenGenerell["Einwohnerdichte"][quartier-1]
    index= int(buildingID[1:])-1
    with dbf.Table(path+'internal_loads.dbf') as table:
        table.open(dbf.READ_WRITE) #open dbf file with write privileges
        areasum = 0
        for key,val in dic_Buildings.items():
            if datenBuildings['Quartier'][int(key[1:])-1] != "Innenhof": 
                areasum += data["geometry"][int(key[1:])-1].area * data["floors_ag"][int(key[1:])-1]

        val = dic_Buildings[buildingID]
        area = data["geometry"][index].area * data["floors_ag"][index] * val
        areaPerPerson = areasum / personen * val + (1-val) * PersProm2

        floors = data["floors_ag"][index]
        area = data["geometry"][index].area
        typ = datenBuildings["Art Nutzung"][index]
        buildingPersonen = (area*floors) / areaPerPerson 
        wwVerbrauch = CalcWWVerbrauch(area= area, buildingPersonen= buildingPersonen, typ= typ, floors= floors)
         
        if datenBuildings['Quartier'][int(buildingID[1:])-1] != "Innenhof":         
            with table[index] as rec:
                rec.OCC_M2P = areaPerPerson
                rec.VWW_LDP = wwVerbrauch
                rec.VW_LDP = wwVerbrauch * 4                
                rec.QCRE_WM2 = GetCoolingDemand(area= area, floors= floors, typ= typ)[0]
                rec.ED_WM2 = GetCoolingDemand(area= area, floors= floors, typ= typ)[1]
                rec.EPRO_WM2 = GetCoolingDemand(area= area, floors= floors, typ= typ)[2]
        else:
            with table[index] as rec:
                rec.OCC_M2P = 0
                rec.VWW_LDP = 0
                rec.VW_LDP = 0               
                rec.QCRE_WM2 = 0
                rec.ED_WM2 = 0
                rec.EPRO_WM2 = 0

def EditSupplySystems2(buildingID, path= ""):
    with dbf.Table(path+'supply_systems.dbf') as table:
        table.open(dbf.READ_WRITE) #open dbf file with write privileges
        index = datenBuildings.index[datenBuildings['Gebäude'] == buildingID].tolist()[0]
        if datenBuildings["Kühlung"][index] == "Ja":
            index2= int(buildingID[1:])-1
            with table[index2] as rec:
                rec.TYPE_CS = "SUPPLY_COOLING_AS1"
        if datenBuildings["Art Heizung"][index] == "Fernwärme":
            index2= int(buildingID[1:])-1
            with table[index2] as rec:
                rec.TYPE_DHW = "SUPPLY_HOTWATER_AS9"
                rec.TYPE_HS = "SUPPLY_HEATING_AS9"
        else:
            index2= int(buildingID[1:])-1
            with table[index2] as rec:
                rec.TYPE_DHW = "SUPPLY_HOTWATER_AS3"
                rec.TYPE_HS = "SUPPLY_HEATING_AS3"

def EditSupplySystems(buildingID, path= ""):
    with dbf.Table(path+'supply_systems.dbf') as table:
        table.open(dbf.READ_WRITE) #open dbf file with write privileges
        index = datenBuildings.index[datenBuildings['Gebäude'] == buildingID].tolist()[0]
        if datenBuildings["Kühlung"][index] == "Ja":
            index2= int(buildingID[1:])-1
            with table[index2] as rec:
                rec.TYPE_CS = "SUPPLY_COOLING_AS1"
        if datenBuildings["Art Heizung"][index] == "Fernwärme":
            index2= int(buildingID[1:])-1
            with table[index2] as rec:
                rec.TYPE_DHW = "SUPPLY_HOTWATER_AS9"
                rec.TYPE_HS = "SUPPLY_HEATING_AS9"
        else:
            index2= int(buildingID[1:])-1
            with table[index2] as rec:
                rec.TYPE_DHW = "SUPPLY_HOTWATER_AS3"
                rec.TYPE_HS = "SUPPLY_HEATING_AS3"


def EditAirConditioning(buildingID, path= ""):
    with dbf.Table(path+'air_conditioning.dbf') as table:
        table.open(dbf.READ_WRITE) #open dbf file with write privileges
        
        index = datenBuildings.index[datenBuildings['Gebäude'] == buildingID].tolist()[0]
        if datenBuildings["Lüftung"][index] == "Ja":
            with table[index] as rec:
                rec.TYPE_VENT = "HVAC_VENTILATION_AS1"
        if datenBuildings["Kühlung"][index] == "Ja":
            with table[index] as rec:
                rec.TYPE_CS = "HVAC_COOLING_AS3"



def GetQuartierInfo(buildingID, path= ""):
    quartier = datenBuildings['Quartier'][datenBuildings.index[datenBuildings['Gebäude'] == buildingID].tolist()[0]]
    buildings = datenBuildings.index[datenBuildings['Quartier'] == quartier].tolist()

    dic_Buildings = {}

    with dbf.Table(path+'typology.dbf') as table:
        for building in buildings:
            for use,percent in zip(["1ST_USE"],["1ST_USE_R"]):
                if getattr(table[building],use).replace(" ","") == "MULTI_RES":
                    dic_Buildings[f'B{str(building+1).zfill(3)}'] = getattr(table[building],percent)
                else:
                    dic_Buildings[f'B{str(building+1).zfill(3)}'] = 0
    return dic_Buildings, quartier



def GetTypology(path="")->dict:
    with dbf.Table(path+'typology.dbf') as table:
        for buildingID in range(1,179):
            buildingID = f'B{str(buildingID).zfill(3)}'
            #print(buildingID)
            
            EditInternalLoads(buildingID= buildingID)
            EditSupplySystems(buildingID= buildingID)
            EditAirConditioning(buildingID= buildingID)

liBaujahre = []
def CalcSanierung(quartier:int, currentYear) -> int:
    baujahr = random.randint(baujahre[datenGenerell["Bauzeit"][quartier-1]][0],baujahre[datenGenerell["Bauzeit"][quartier-1]][1])
    liBaujahre.append(baujahr)
    sanJahr = baujahr + floor((currentYear-baujahr)/Sanierungszyklus) * Sanierungszyklus
    return sanJahr

def GetQuartiersNummer(building:str)->int:
    return int(datenBuildings.loc[datenBuildings['Gebäude'] == building]["Quartier"])

def GetTimeline(sanJahr:int) -> str:
    for key,val in timelines.items():
        if sanJahr in range(val[0],val[1]):
            return key

def GetValue(building:str, currentYear) -> str:
    quartier= GetQuartiersNummer(building= building)

    sanJahr= CalcSanierung(quartier, currentYear= currentYear)    
    sanQual = GetTimeline(sanJahr)   
    return sanQual

GetTypology()

def AddVentilation(buildingID, path):
    with dbf.Table(path+'air_conditioning.dbf') as table:
        table.open(dbf.READ_WRITE) #open dbf file with write privileges
        index= int(buildingID[1:])-1
        with table[index] as rec:
            rec.TYPE_VENT = "HVAC_VENTILATION_AS2"
            rec.TYPE_CTRL = "HVAC_CONTROLLER_AS2"


def EditArchitecture(currentYear, path= ""):
    with dbf.Table(path+'architecture.dbf') as table:
        table.open(dbf.READ_WRITE) #open dbf file with write privileges
        for i,record in enumerate(dbf.Process(table)): #iterate entries
            #print(f"Building: {record.NAME}")
            sanQual = GetValue(building= record.name.replace(" ",""), currentYear= currentYear)

            record.TYPE_FLOOR = "FLOOR_"+sanQual
            record.TYPE_PART = "WALL_"+sanQual
            record.TYPE_BASE = "FLOOR_"+sanQual
            record.TYPE_ROOF = "ROOF_"+sanQual
            record.TYPE_WALL = "WALL_"+sanQual
            record.TYPE_WIN = "WINDOW_"+sanQual

            if sanQual == "2030+":
                buildingID = f'B{str(i).zfill(3)}'
                AddVentilation(buildingID, path)

    inter = pd.DataFrame(liBaujahre)
    #print(inter.info())
    inter.to_csv("Baujahre.csv")
