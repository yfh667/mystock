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

if __name__ == '__main__':


    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = findroot.find_project_root(current_dir)
    DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")

    db_folder = DATA_FOLDER + '/cex'  # 数据库存储文件夹
    db_name_raw = "mexc_spot_REAL" + '.db'  # 数据库文件名
    db_mubiao_name = "spotold" + '.db'
    flag = 0






    db = cexdb.CexSQLiteDatabase(db_folder, db_name_raw)

    db.connect()

    tokens = db.readdbtoken()

    creattime_want = one_geck.datetime_to_timestamp(2024, 1, 1, 0, 0, 0, is_utc=True)

    usetoken = []
    for token in tokens:


        creattime_token = timedefine.datetime_to_timestamp_str(token.creattime)
        if(creattime_token>creattime_want ):
            usetoken.append(token)
    print (usetoken)
    db.close()


   # db_mubiao_name = "myspot" + '.db'
    db = cexdb.CexSQLiteDatabase(db_folder, db_mubiao_name)
    db.connect()
    db.insert_Multidata(usetoken)

    start_timestamp =creattime_want
    end_timestamp = timedefine.get_current_utc_timestemp()

    kline = 'W'
    aggregate =1
    queues = []

    for token in usetoken:
        queue = mexc_queue.mexc_create_request_queue(token.name, start_timestamp, end_timestamp, kline, aggregate)
        queues.extend(queue)


    rate =0.3
    capacity = 20
    max_threads_per_proxy = 1
    clash_api_url = "http://127.0.0.1:9097"
    headers = {"Authorization": "Bearer 123"}

    startport = 50000


    proxys = proxymultitheread.get_one_ip_proxy_multithread(startport, clash_api_url, headers)
    task_manager = mexcovhl_parall.MexcOvhlTaskManager(
        queues,
        proxys,
        rate,
        capacity,
        max_threads_per_proxy,
        flag
    )


    results, failed_tasks = task_manager.run()
   # print(results)

    # 打印实例属性
    token_price_history_list = db.collect_ovhl_data(results)
    db.insert_multiple_price_history(token_price_history_list)


    db.close()

