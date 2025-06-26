import  dexprice.modules.gateio.cexprice as gateprice
import  dexprice.modules.cexdb.cexdb as cexdb
import  time
import dexprice.modules.OHLCV.one_geck as one_geck


import  dexprice.modules.utilis.define as define
import  dexprice.modules.gateio.queuefortoken as queuefortoken
import dexprice.modules.gateio.gateio_parrel2 as gateio_parrel2
import dexprice.modules.proxy.proxymultitheread as proxymultitheread

if __name__ == "__main__":


    db_folder = '/Users/admin/Desktop/dexprice/MarketSystem/Data/Project'   # 数据库存储文件夹
    db_name = "test4"+'.db'  # 数据库文件名
    db = cexdb.CexSQLiteDatabase(db_folder, db_name)

    db.connect()
    # 创建一个 Tokendb 实例



    # 创建一个 Tokendb 实例
    token = define.CexTokenInfo(
        name="TOMA",            # Token name (string)
        chainid="USD",     # Chain ID (string)


    )
    tokens = []
    tokens.append(token)
    db.insert_Multidata(  tokens)

    tokens = db.readdbtoken()
    # 打印实例属性



    current = []
    for token in tokens:
        current.append(token.name)



    # 生成开始和结束时间的时间戳
    start_timestamp = one_geck.datetime_to_timestamp(2024, 12, 20, 20, 0, 0, is_utc=True)
    end_timestamp = one_geck.datetime_to_timestamp(2024, 12, 29, 12, 0, 0, is_utc=True)
    kline = 'h'
    aggregate = '4'


    queue = queuefortoken.create_request_queue(current[0], start_timestamp, end_timestamp, kline, aggregate)
    print(queue)




    rate =0.5
    capacity = 30

    clash_api_url = "http://127.0.0.1:9097"
    headers = {"Authorization": "Bearer 123"}

    startport = 50000


    proxys = proxymultitheread.get_one_ip_proxy_multithread(startport, clash_api_url, headers)

    max_threads_per_proxy = 1


    task_manager = gateio_parrel2.GateTaskManager2(queue,    proxys, rate, capacity, max_threads_per_proxy)
    results, failed_tasks = task_manager.run()



    token_price_history_list = db.collect_ovhl_data(results)
    # 批量插入数据
    db.insert_multiple_price_history(token_price_history_list)


    db.close()