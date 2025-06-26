
import  dexprice.modules.utilis.define as define

import dexprice.modules.db.insert_db as insert_db
import os
import dexprice.modules.utilis.findroot as findroot
import dexprice.modules.db.multidb as multidb
import dexprice.modules.OHLCV.constructTokenPriceSummar as constructTokenPriceSummar
## use postql, we could neleget it
if __name__ == "__main__":

    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = findroot.find_project_root(current_dir)
    DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")

    chain_id = "solana"
    # db_folder = '/Users/admin/Desktop/dexprice/MarketSystem/Data/Project'   # 数据库存储文件夹
    db_folder = DATA_FOLDER+'/Project'
    db_name = "chill"+'.db'  # 数据库文件名
    db = insert_db.SQLiteDatabase(db_folder, db_name)

    db.connect()

    tokens = db.readdbtoken()
    requestedtokenid = []
    for token in tokens:
        requestedtokenid.append(token.tokenid)

    db_path = db_folder+'/'+db_name
    task_manager = multidb.DatabaseReadTaskManager(requestedtokenid,  db_path, max_threads=6)
    results = task_manager.run()
    tokenhistorys = []
    # 处理结果
    for token_id, rows in results:
        tokenhistory=[]
        for row in rows:
            test = define.TokenPriceHistory(row[1],row[2],row[3],row[4],row[5],row[6],row[7])
            tokenhistory.append(test)
        tokenhistorys.append(tokenhistory)

    rawdata = tokenhistorys[0]
    t = constructTokenPriceSummar.mergeTokenHistoryByTimefr(rawdata,'15min')
    print(t)
