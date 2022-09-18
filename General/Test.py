# -*- coding: cp1252 -*-




import dbf

zuhause = "C:/Users/mariu/EK/1/outputs/data/demand/"
if 0:
    with dbf.Table("C:/Users/mariu/source/repos/General/General/Scenarios/2024/Prio Fernwärme/architecture.dbf") as table_FW:
        with dbf.Table("C:/Users/mariu/source/repos/General/General/Scenarios/2024/Prio Wärmepumpe/architecture.dbf") as table_WP:
            table_FW.open(dbf.READ_WRITE) #open dbf file with write privileges
            table_WP.open(dbf.READ_WRITE) #open dbf file with write privileges
            for index in range(178): #iterate entries
                with table_FW[index] as rec_FW:
                    with table_WP[index] as rec_WP:
                        if rec_WP.TYPE_WALL != rec_FW.TYPE_WALL: print(f'B{str(index+1).zfill(3)}')
                        #record.TYPE_FLOOR = "FLOOR_"+sanQual
                        #record.TYPE_PART = "WALL_"+sanQual
                        #record.TYPE_BASE = "FLOOR_"+sanQual
                        #record.TYPE_ROOF = "ROOF_"+sanQual
                        #record.TYPE_WALL = "WALL_"+sanQual
                        #record.TYPE_WIN = "WINDOW_"+sanQual


with dbf.Table("C:/Users/mariu/source/repos/General/General/Scenarios/2050/Prio Wärmepumpe/supply_systems.dbf") as table:
    table.open(dbf.READ_WRITE) #open dbf file with write privileges
    for index in range(178): #iterate entries
        with table[index] as rec:
            if rec.TYPE_HS.replace(" ","") == "SUPPLY_HEATING_AS3": print(f'B{str(index+1).zfill(3)}')
