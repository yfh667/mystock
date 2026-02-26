
import dexprice.modules.proxy.proxymultitheread as proxymultitheread


import dexprice.modules.biance.cex_queue as cex_queue
from datetime import datetime, timezone
import dexprice.modules.biance.binancecovhl_parall as binancecovhl_parall
import dexprice.modules.cexdb.multidb    as multidb

import dexprice.modules.utilis.define as define
import datetime
import dexprice.modules.cexdb.cexdb as cexdb

import os
import dexprice.modules.utilis.findroot as findroot







if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = findroot.find_project_root(current_dir)
    DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")





    db_folder = DATA_FOLDER + '/cex'  # 数据库存储文件夹


    #
    # db_name = "mexc_contract" + '.db'  # 数据库文件名
    # db = cexdb.CexSQLiteDatabase(db_folder, db_name)
    #
    # db.connect()
    #
    # # symbol = getalltoken.getalltoken()
    # symbol = [t for t in getalltoken.getalltoken()
    #           if "STOCK" not in t.upper() and t.endswith("_USDT")]
    #
    # # symbol  = ['BTC','SOL']
    # tokens = []
    # filtered = [t for t in symbol if "STOCK" not in t.upper()]
    # symbol = filtered
    # rate = 0.3
    # capacity = 10
    # max_threads_per_proxy = 1
    # clash_api_url = "http://127.0.0.1:9097"
    # headers = {"Authorization": "Bearer manba"}
    #
    # startport = 50000
    #
    # proxys = proxymultitheread.get_one_ip_proxy_multithread(startport, clash_api_url, headers)
    #
    # task_manager = initial_timesta_parall.MexcTaskManager(
    #     symbol,
    #     proxys,
    #     rate,
    #     capacity,
    #     max_threads_per_proxy,
    #
    # )
    # results, failed_tasks = task_manager.run()
    # print(results)
    #
    # db.insert_Multidata(results)
    # # 打印实例属性
    #
    # db.close()
    # and we insert into the db

    # here we could just use one token

    kline = 'H'
    aggregate = 1



    db_name_raw = "binance_contract" + '.db'  # 数据库文件名


    flag = 'futures'

    db = cexdb.CexSQLiteDatabase(db_folder, db_name_raw)

    db.connect()

    tokens = db.readdbtoken()



    # db.close()
# we get the token





   # price_time_want = one_geck.datetime_to_timestamp(2025, 6, 28, 0, 0, is_utc=True)

    # price_time_want = one_geck.datetime_to_timestamp(2025, 6, 24, 0, 0, 0, is_utc=True)
    # 获取当前时间的 UTC 时间戳
    # current_time = datetime.datetime.utcnow()
    # current_time = current_time- datetime.timedelta(days=1)
    # 计算前两天的时间

    # current_time = one_geck.datetime_to_timestamp(2025, 7 , 2, 0, 0, is_utc=True)

    # two_days_ago = current_time - datetime.timedelta(days=2)

   #  # 将其转换为时间戳格式
   #  start_timestamp = two_days_ago.timestamp()
   #
   #  end_dt = datetime.datetime(2026, 2, 26, 0, 0, 0, tzinfo=datetime.timezone.utc)
   #  # 2. 用 datetime 对象减去 timedelta 对象
   #  start_dt = end_dt - datetime.timedelta(days=7)
   # # end_timestamp = one_geck.datetime_to_timestamp(2026, 2, 26, 0, 0, 0, is_utc=True)

    # 3. 最后再转换成时间戳 (int)

    start_dt = datetime.datetime(2026, 2, 22, tzinfo=timezone.utc)
    end_dt = datetime.datetime(2026, 2, 26, tzinfo=timezone.utc)


    start_timestamp = int(start_dt.timestamp())
    end_timestamp = int(end_dt.timestamp())




    ##
    queues = []

    max_limit=1500
    for token in tokens:
        queue = cex_queue.cexkline_create_request_queue(token.name,start_timestamp, end_timestamp,kline,aggregate,max_limit)
        queues.extend(queue)

    rate = 0.3
    capacity = 20
    max_threads_per_proxy = 1
    clash_api_url = "http://127.0.0.1:9097"
    headers = {"Authorization": "Bearer manba"}

    startport = 50000

    proxys = proxymultitheread.get_one_ip_proxy_multithread(startport, clash_api_url, headers)
    cexlimit=1500
    cexname = 'binance'
    task_manager = binancecovhl_parall.BinanceOvhlTaskManager(
        queues,
        proxys,
        rate,
        capacity,
        max_threads_per_proxy,
        flag,
        cexlimit,
        cexname
    )

    results, failed_tasks = task_manager.run()
    # print(results)

    # 打印实例属性
    token_price_history_list = db.collect_ovhl_data(results)
    db.insert_multiple_price_history(token_price_history_list)

    #
    tokens = db.readdbtoken()
    ## 读取token的历史数据，进行处理
    db_path = db_folder + '/' + db_name_raw

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
    print(1)
    db.close()

