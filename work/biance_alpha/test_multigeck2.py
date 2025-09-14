
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
    db_new_path = os.path.join(db_folder, db_name)

    copy_sqlite_db(db_raw_path, db_new_path)

    db = insert_db.SQLiteDatabase(db_folder, db_name)
    db.connect()


    timeframe = "day"  # 可选值: day, hour, minute
    aggregate = "1"  # 聚合时间段
    startport = 50000
    geck_limit = 7


    clash_api_url = "http://127.0.0.1:9097"
    headers = {"Authorization": "Bearer manba"}


    tokendata = db.readdbtoken()


    # 初始化字典，用链名作为键，地址列表作为值
    chain_addresses = {
     'solana': [],
     'base': [],
     'ethereum': [],
     'bsc': []
    }
    startport = 50000


    current_time = datetime.datetime.utcnow()


    before_timestamp = current_time
   # before_timestamp = current_time - datetime.timedelta(days=5)





    before_timestamp = before_timestamp.timestamp()
    before_timestamp = int(before_timestamp)





    # before_timestamp = 1754744898


    # 遍历 token_new，根据链名将地址加入对应的列表
    for token in tokendata:
     # 确保 token.chainid 是链名，并存在于字典的键中
     if token.chainid in chain_addresses:
      chain_addresses[token.chainid].append(token.pair_address)  # 添加地址到对应链的列表

    for chain, pairaddresses in chain_addresses.items():
         print(f"we check Chain: {chain} ")
         proxys = proxymultitheread.get_one_ip_proxy_multithread_geck(startport, clash_api_url, headers)
         if chain == "ethereum":
          chainid = 'eth'
         else:
          chainid = chain
         geckpricehistory.inserthistorywithgeck_db(db, pairaddresses, chainid, proxys, timeframe,
                                                   aggregate, before_timestamp, geck_limit)

    # chainid = 'bsc'
    # clash_api_url = "http://127.0.0.1:9097"
    # headers = {"Authorization": "Bearer manba"}
    # proxys = proxymultitheread.get_one_ip_proxy_multithread_geck(startport, clash_api_url, headers)
    # geckpricehistory.inserthistorywithgeck_db(db, pairaddresses, chainid, proxys, timeframe,
    #                                           aggregate, before_timestamp, geck_limit)
    #
    # tokens = db.readdbtoken()
    # ## 读取token的历史数据，进行处理
    # db_path = db_folder + '/' + db_name + '.db'
    #


    db.close()


if __name__ == "__main__":
    main()
