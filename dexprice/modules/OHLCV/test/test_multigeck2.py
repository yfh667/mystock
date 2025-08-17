import dexprice.modules.PriceMonitor.dexscreen_parrel as dexscreen_parrel
import dexprice.modules.utilis.define as define
import dexprice.modules.utilis.define as define
import dexprice.modules.proxy.proxydefine as proxydefine
import dexprice.modules.db.insert_db as insert_db
import dexprice.modules.proxy.clash_api as clash
import dexprice.modules.proxy.testproxy as testproxy
import dexprice.modules.OHLCV.geck_parrel as geck_parrel
import dexprice.modules.proxy.proxymultitheread as proxymultitheread
import os
import dexprice.modules.utilis.findroot as findroot

def main():
   # addresses = ["6USpEBbN94DUYLUi4a2wo3AZDCyozon1PLGYu27jzPkX"]  # 您的地址列表

    addresses = ["0xc23db46993f643f1fa0494cd30f9f43505885d84",
                 "0x7cCC3010e52fbca54467ff68eEc4be78420571C5",
    ]

    chain_id = "bsc"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = findroot.find_project_root(current_dir)
    DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")

    db_folder = DATA_FOLDER+'/Project'  # 数据库存储文件夹
    db_name = "testgck" + '.db'  # 数据库文件名
    db = insert_db.SQLiteDatabase(db_folder, db_name, "solana")
    db.connect()

    rate = 5
    capacity = 300
    sourcetype = define.Config.DEXS
    max_threads_per_proxy = 3
    clash_api_url = "http://127.0.0.1:9097"
    headers = {"Authorization": "Bearer 123"}

    startport = 50000
    proxys = proxymultitheread.get_one_ip_proxy_multithread(startport, clash_api_url, headers)





    task_manager = dexscreen_parrel.TaskManager(addresses, sourcetype, chain_id, proxys, rate, capacity,
                                                max_threads_per_proxy)
    tokensinfo, failed_tasks = task_manager.run()
    db.insert_multiple_tokeninfo(tokensinfo)

    timeframe = "day"  # 可选值: day, hour, minute
    aggregate = "1"  # 聚合时间段
    before_timestamp = "1730678400"  # 可选的时间戳参数
    limit = 100

    rate = 0.5
    capacity = 30

    max_threads_per_proxy = 1

    task_manager = geck_parrel.GeckTaskManager(addresses, chain_id, proxys, rate, capacity, max_threads_per_proxy,
                                               timeframe, aggregate, before_timestamp, limit)
    results, failed_tasks = task_manager.run()
    for ovhldata in results:
        db.insert_OvhlFromDex(ovhldata)
    print(f"Total failed tasks: {failed_tasks}")
    print(f"Total successful results: {len(results)}")
    print(f"Total failed tasks: {len(failed_tasks)}")
    db.close()


if __name__ == "__main__":
    main()
