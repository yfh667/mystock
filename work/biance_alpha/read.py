
import dexprice.modules.db.insert_db as insert_db
import dexprice.modules.proxy.clash_api as clash
import dexprice.modules.proxy.testproxy as testproxy
import dexprice.modules.OHLCV.geck_parrel as geck_parrel
import dexprice.modules.proxy.proxymultitheread as proxymultitheread
import os
import time
import dexprice.modules.allmodules.geckpricehistory as geckpricehistory
import dexprice.modules.utilis.findroot as findroot
import datetime
import sqlite3

import dexprice.modules.db.multidb as multidb
from dexprice.modules.utilis import define


def copy_sqlite_db(src_path, dst_path):
 os.makedirs(os.path.dirname(dst_path), exist_ok=True)
 with sqlite3.connect(src_path) as src_conn:
  with sqlite3.connect(dst_path) as dst_conn:
   src_conn.backup(dst_conn)  # 直接用 SQLite 自带的 backup API
 print(f"Database copied from {src_path} -> {dst_path}")


def main():
   # addresses = ["6USpEBbN94DUYLUi4a2wo3AZDCyozon1PLGYu27jzPkX"]  # 您的地址列表
    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = findroot.find_project_root(current_dir)
    DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")
   # pairaddresses = ["0x7F0B9A92fe7ABBC64d38cbD02a3c39191657b8bB",
   #               "0x7cCC3010e52fbca54467ff68eEc4be78420571C5",
   #  ]

    # 示例用法
    db_folder_raw =  DATA_FOLDER + '/cex/alpha'
    db_raw_path = os.path.join(db_folder_raw, "biance_alpha.db")

    #db_folder = os.path.join(DATA_FOLDER, "/cex/alpha/history")
    db_folder = DATA_FOLDER+'/cex/alpha/history'  # 数据库存储文件夹
    db_name = "alpha_history.db"


    db = insert_db.SQLiteDatabase(db_folder, db_name)
    db.connect()

    tokens = db.readdbtoken()
    ## 读取token的历史数据，进行处理
    db_path = db_folder + '/' + db_name

    requestedtokenid = []
    for token in tokens:
        requestedtokenid.append(token.tokenid)

    task_manager = multidb.DatabaseReadTaskManager(requestedtokenid, db_path, max_threads=5)
    results = task_manager.run()
    tokenhistorys = []
    # 处理结果
    for token_id, rows in results:
        tokenhistory = []
        for row in rows:
            test = define.TokenPriceHistory(row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            tokenhistory.append(test)
        tokenhistorys.append(tokenhistory)

    find_address = []

    for tokenhistory in tokenhistorys:
        if (len(tokenhistory) > 1):
                    token = tokenhistory[-1]
                    num = 0
                    all_size  = 0
                    for i in range(len(tokenhistory)-1):
                        num = num+1
                        all_size = all_size+tokenhistory[i].volume
                    avare_size = all_size/num

                    if token.volume>5*avare_size:
                        tokenid = tokenhistory[0].tokenid
                        tokendb = db.read_token_withid(tokenid)
                        pairaddress = tokendb.pair_address
                        find_address.append(pairaddress)



    unique_find_address = list(set(find_address))
    for address in unique_find_address:
        print(address)
    # db.close()





if __name__ == "__main__":
    main()
