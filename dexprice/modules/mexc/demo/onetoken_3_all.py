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

import dexprice.modules.strategy.basefunction as basefunction
if __name__ == '__main__':


    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = findroot.find_project_root(current_dir)
    DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")

    db_folder = DATA_FOLDER + '/cex'  # 数据库存储文件夹
 #   db_name_raw = "mexc_spot" + '.db'  # 数据库文件名
  #  db_mubiao_name = "daddt" + '.db'
  #  db_name_raw = "mexc_contract" + '.db'  # 数据库文件名
    db_mubiao_name = "Strategt1" + '.db'
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

    for tokenhistory in tokenhistorys:
        sorthistory = basefunction.sort_by_time(tokenhistory)
        days = len(sorthistory)
        tokenid  = sorthistory[0].tokenid

        baches_7 =days//7
        amout_arrary = []

        for i in range(baches_7):
            index = days-i*7-1
            amout = 0

            for j in range(7):
                amout = amout+sorthistory[index-j].amount




            amout_arrary.append(amout)

        if(len(amout_arrary)>2):
            if (amout_arrary[0] > 2 * amout_arrary[1]):


                symbol = db.read_token_withid(tokenid).name
                print(f"we find { symbol}")




    print("helo")
    db.close()