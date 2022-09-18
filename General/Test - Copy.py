# -*- coding: cp1252 -*-




import dbf
import pandas as pd


building = pd.read_csv("C:/Users/mariu/EK/1/outputs/data/demand/Total_demand.csv", sep= ",", decimal= ".")
building.to_csv("test.csv", sep= ";", decimal= ",")

building = pd.read_csv("C:/Users/mariu/EK/1/outputs/data/demand/B001.csv", sep= ",", decimal= ".")
building.to_csv("testGeb.csv", sep= ";", decimal= ",")