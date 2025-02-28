import pandas as pd
import requests


import dexprice.modules.mexc.gettoken_spot as getalltoken
import dexprice.modules.cexdb.cexdb as cexdb

import dexprice.modules.utilis.define as define
import os
import dexprice.modules.utilis.findroot as findroot
import dexprice.modules.mexc.initial_timesta_spot as initial_timesta
import dexprice.modules.mexc.initial_timesta_parall_spot as initial_timesta_parall
import dexprice.modules.proxy.proxymultitheread as proxymultitheread


def extract_tokens(csv_path):
    """从CSV文件中提取代币列表"""
    # 读取CSV文件（无header模式）
    df = pd.read_csv(csv_path, header=None)

    # 提取第一列的所有交易对
    trading_pairs = df[0].tolist()[1:]  # 跳过标题行



    return list(set(trading_pairs))  # 去重后返回


if __name__ == '__main__':


    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = findroot.find_project_root(current_dir)
    DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")

    db_folder = DATA_FOLDER + '/cex'  # 数据库存储文件夹
    db_name = "mexc_spot_REAL" + '.db'  # 数据库文件名
    db = cexdb.CexSQLiteDatabase(db_folder, db_name)

    db.connect()
    # 使用示例

    csv_path = "/Users/admin/Desktop/single-dex/Data/cex/mexc.csv"

    # 提取代币列表
    tokens = extract_tokens(csv_path)
    print("提取到的代币:", tokens)

#    symbol = getalltoken.getalltoken()
   # symbol  = ['BTC','SOL']


    symbol = []

    for token in tokens:
        symbol.append(token+'USDT')

    rate =0.3
    capacity = 20
    max_threads_per_proxy = 1
    clash_api_url = "http://127.0.0.1:9097"
    headers = {"Authorization": "Bearer 123"}

    startport = 50000


    proxys = proxymultitheread.get_one_ip_proxy_multithread(startport, clash_api_url, headers)

    task_manager = initial_timesta_parall.MexcTaskManager(
        symbol,
        proxys,
        rate,
        capacity,
        max_threads_per_proxy,

    )
    results, failed_tasks = task_manager.run()
    print(results)

    db.insert_Multidata(results)
    # 打印实例属性

    db.close()
    # and we insert into the db
