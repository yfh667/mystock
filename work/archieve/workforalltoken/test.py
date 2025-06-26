import  dexprice.modules.utilis.define as define
import pandas as pd

import dexprice.modules.db.insert_db as insert_db

import dexprice.modules.db.multidb as multidb
if __name__ == "__main__":

    chain_id = "solana"
    db_folder = '/home/yfh/Desktop/MarketSystem/Data/Project'   # 数据库存储文件夹
    db_name = "solanaallday"+'.db'  # 数据库文件名
    db = insert_db.SQLiteDatabase(db_folder, db_name,chain_id)
    db.connect()

    tokens = db.readdbtoken()
    requestedtokenid = []
    for token in tokens:
        requestedtokenid.append(token.tokenid)

    db_path = db_folder+'/'+db_name
    task_manager = multidb.DatabaseReadTaskManager(requestedtokenid,  db_path,chain_id, max_threads=6)
    results = task_manager.run()
    tokenhistorys = []
    # 处理结果
    for token_id, rows in results:
        tokenhistory=[]
        for row in rows:
            test = define.TokenPriceHistory(row[1],row[2],row[3],row[4],row[5],row[6],row[7])
            tokenhistory.append(test)
        tokenhistorys.append(tokenhistory)
   # print(tokenhistorys)
    #print(rawdata)
    import  dexprice.modules.strategy.monotonic as  star1
    import dexprice.modules.strategy.normal as normal

    for tokenhistory in tokenhistorys:

        dates, opens, highs, lows, closes = normal.checknormalgui(tokenhistory)
        if(star1.monotonic_intervals(dates, opens, highs, lows, closes)):
         #   print( f"we find{tokenhistory[0].tokenid}")
            if(db.read_token_withid(tokenhistory[0].tokenid)):
                print( f"we find  { db.read_token_withid(tokenhistory[0].tokenid).pair_address}")


        else :
            pass



