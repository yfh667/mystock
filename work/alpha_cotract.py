
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
    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = findroot.find_project_root(current_dir)
    DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")

    # 示例用法
    db_folder_raw =  DATA_FOLDER + '/cex'
    db_raw_path = os.path.join(db_folder_raw, "biance_alpha.db")

    #db_folder = os.path.join(DATA_FOLDER, "/cex/alpha/history")
    db_folder = DATA_FOLDER+'/cex/alpha/history'  # 数据库存储文件夹
    db_name = "alpha_history.db"


    db = insert_db.SQLiteDatabase(db_folder, db_name)
    db.connect()

    alpha_tokens = db.readdbtoken()
    db.close()



    # 示例用法

    db_folder = DATA_FOLDER + '/cex'  # 数据库存储文件夹
    db_name = "binance_contract.db"

    db = insert_db.SQLiteDatabase(db_folder, db_name)
    db.connect()

    contract_tokens = db.readdbtoken()
    db.close()


    real_contract_names = []

    for token in contract_tokens:
        name = token.name
        realname = name.replace('_USDT', '')
        real_contract_names.append(realname)


    real_alpha_name = []
    for token in alpha_tokens:
        name = token.name
        real_alpha_name.append(name)

    common_elements = list(set(real_contract_names) & set(real_alpha_name))

    print(common_elements)

    # he r




if __name__ == "__main__":
    main()
