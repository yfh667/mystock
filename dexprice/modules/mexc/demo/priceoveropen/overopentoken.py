import dexprice.modules.mexc.getalltoken as getalltoken
import dexprice.modules.cexdb.cexdb as cexdb

import dexprice.modules.utilis.define as define
import os
import dexprice.modules.utilis.findroot as findroot
import dexprice.modules.mexc.initial_timesta as initial_timesta
import dexprice.modules.mexc.initial_timesta_parall as initial_timesta_parall
import dexprice.modules.proxy.proxymultitheread as proxymultitheread
import dexprice.modules.utilis.timedefine as timedefine
from dexprice.three import creattime
import dexprice.modules.OHLCV.one_geck as one_geck
import dexprice.modules.mexc.mexc_queue as mexc_queue
import dexprice.modules.mexc.mexcovhl_parall as mexcovhl_parall
import  dexprice.modules.cexdb.multidb as multidb
import dexprice.modules.mexc.getalltoken as getalltoken
import dexprice.modules.cexdb.cexdb as cexdb
import dexprice.modules.tg.tgbot as tgbot
import dexprice.modules.tg.mexctg as mexctg
import dexprice.modules.utilis.define as define
import dexprice.modules.utilis.define as define
import os
import dexprice.modules.utilis.findroot as findroot
import time
import threading
import dexprice.modules.strategy.basefunction as basefunction
if __name__ == '__main__':


    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = findroot.find_project_root(current_dir)
    DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")

    db_folder = DATA_FOLDER + '/cex'  # 数据库存储文件夹
 #   db_name_raw = "mexc_spot" + '.db'  # 数据库文件名
  #  db_mubiao_name = "daddt" + '.db'
  #  db_name_raw = "mexc_contract" + '.db'  # 数据库文件名
    db_mubiao_name = "spotold" + '.db'
  #  flag = 1


    db = cexdb.CexSQLiteDatabase(db_folder, db_mubiao_name)

    db.connect()

    tokens = db.readdbtoken()
    requestedtokenid = []
    for token in tokens:
        requestedtokenid.append(token.tokenid)





    db_path = db_folder+'/'+db_mubiao_name



    task_manager = multidb.CexDatabaseReadTaskManager(requestedtokenid,  db_path, max_threads=6)
    results = task_manager.run()
    tokenhistorys = []
    # 处理结果
    for token_id, rows in results:
        tokenhistory=[]
        for row in rows:
            test = define.CexTokenPriceHistory(row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8])
            tokenhistory.append(test)
        tokenhistorys.append(tokenhistory)
    tokens = []
    for tokenhistory in tokenhistorys:
        sorthistory = basefunction.sort_by_time(tokenhistory)
        length = len(sorthistory)


        if length > 1:
            tokenid = sorthistory[0].tokenid
            token = db.read_token_withid(tokenid)
            if sorthistory[-1].close>sorthistory[0].open:
                if   sorthistory[-1].close>sorthistory[0].close:
                    tokens.append(token)
                    print(f"we find {token.name}")
                    continue



    #
    print("helo")
    db.close()


    #hre we need inset the tokenids into the new_cex_monitor db

    db_folder = DATA_FOLDER + '/cex/spot_over_open'  # 数据库存储文件夹
    #   db_name_raw = "mexc_spot" + '.db'  # 数据库文件名
    #  db_mubiao_name = "daddt" + '.db'
    #  db_name_raw = "mexc_contract" + '.db'  # 数据库文件名
    db_send= "sended" + '.db'
    db = cexdb.CexSQLiteDatabase(db_folder, db_send)
    db.connect()


    db_raw = db.readdbtoken()

    db_raw_name = []

    for token in db_raw:
        db_raw_name.append(token.name)


    tokenlocalname_set = set(db_raw_name)

    added_tokens = []
    for token in tokens:
            if token.name not in tokenlocalname_set:
                added_tokens.append(token)




    added_tokens = list(set(added_tokens))

    if len(added_tokens)>0:
    # we need insert the add_tokens in the db
        db.insert_Multidata2(added_tokens)
        print(f"helo{added_tokens}")
        mexctg.mexctg2("@jingou11", added_tokens)

    else:
        print("no new_cex_monitor tokens")

    db.close()
