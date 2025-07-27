import dexprice.modules.mexc.getalltoken as getalltoken
import dexprice.modules.cexdb.cexdb as cexdb

import dexprice.modules.utilis.define as define
import os
import dexprice.modules.utilis.findroot as findroot

import  dexprice.modules.cexdb.multidb as multidb

import dexprice.modules.strategy.basefunction as basefunction
if __name__ == '__main__':


    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = findroot.find_project_root(current_dir)
    DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")

    db_folder = DATA_FOLDER + '/cex'  # 数据库存储文件夹
 #   db_name_raw = "mexc_spot" + '.db'  # 数据库文件名
    db_mubiao_name = "mexc_contract_wanted_time_price1D" + '.db'


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


# here is the strategy
    for tokenhistory in tokenhistorys:
        sorthistory = basefunction.sort_by_time(tokenhistory)
        length_his = len(sorthistory)
    # here we could use our strategy .
        if length_his<7:
            continue
        amount = 0
        counts=0

        for i in range(length_his-1):
            amount = amount + sorthistory[i].amount
        avaeg_amoint = amount/(length_his-1)

        if sorthistory[length_his-1].amount>5*avaeg_amoint:
            token = db.read_token_withid(sorthistory[i].tokenid)
            print("yes", token.name, sorthistory[-1].time)

        # for i in range(length_his):
        #     counts=1
        #     allvolume+=sorthistory[i].volume
        #     average = allvolume/length_his
        #     if sorthistory[i].volume>5*average:
        #
        #         if sorthistory[i].volume>5*sorthistory[i-1].volume:
        #
        #
        #             token = db.read_token_withid(sorthistory[i].tokenid)
        #             print("yes", token.name,sorthistory[i].time)
        #
        #             break





    db.close()