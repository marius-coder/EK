# -*- coding: cp1252 -*-




import dbf



with dbf.Table("C:/Users/cermak/source/repos/EK/General/Scenarios/2024/Prio Fernwärme/architecture.dbf") as table_FW:
    with dbf.Table("C:/Users/cermak/source/repos/EK/General/Scenarios/2024/Prio Wärmepumpe/architecture.dbf") as table_WP:
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


