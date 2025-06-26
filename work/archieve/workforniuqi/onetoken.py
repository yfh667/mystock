
import  dexprice.modules.utilis.define as define
import dexprice.modules.db.insert_db as insert_db

import dexprice.modules.PriceMonitor.dexscreen_priceapi as dexscreen_priceapi

import dexprice.modules.OHLCV.one_geck as one_geck
import dexprice.modules.OHLCV.geck_parrel2 as geck_parrel2
import dexprice.modules.proxy.proxymultitheread as proxymultitheread
import dexprice.modules.db.multidb    as multidb

## use postql, we could neleget it
if __name__ == "__main__":

    chain_id = "solana"
    db_folder = '/Users/admin/Desktop/dexprice/MarketSystem/Data/Project'   # 数据库存储文件夹
    db_name = "chill"+'.db'  # 数据库文件名
    db = insert_db.SQLiteDatabase(db_folder, db_name,chain_id)
    db.connect()

    address = ['93tjgwff5Ac5ThyMi8C4WejVVQq4tuMeMuYW1LEYZ7bu']
    # tokens = db.readdbtoken()
    proxy_port = 50000
    tokeninfo = dexscreen_priceapi.Get_Token_Dexscreen(define.Config.DEXS,chain_id,address, proxy_port)
    tokeninfos = []

    tokeninfos.extend(tokeninfo)

    db.insert_multiple_tokeninfo(tokeninfos)

    tokensdata = db.readdbtoken()
    paireaddress = []
    for token in tokensdata:
        paireaddress.append(token.pair_address)

    pool_address = paireaddress
    # 生成开始和结束时间的时间戳
    start_timestamp = one_geck.datetime_to_timestamp(2024, 11, 15, 20, 0, 0, is_utc=True)
    end_timestamp = one_geck.datetime_to_timestamp(2024, 11, 17 , 7, 0, 0, is_utc=True)
    kline = 'hour'
    aggregate = '1'
    currency = "usd"
    token = 'base'

    queue = one_geck.create_request_queue(pool_address, start_timestamp, end_timestamp, kline, aggregate)

    clash_api_url = "http://127.0.0.1:9097"
    headers = {"Authorization": "Bearer 123"}

    startport = 50000

    proxys = proxymultitheread.get_one_ip_proxy_multithread(startport, clash_api_url, headers)

    rate =0.5
    capacity = 30


    max_threads_per_proxy = 1
    task_manager = geck_parrel2.GeckTaskManager2(queue,  chain_id, proxys, rate, capacity, max_threads_per_proxy)
    results, failed_tasks = task_manager.run()
    token_price_history_list = db.collect_ovhl_data(results)
    # 批量插入数据
    db.insert_multiple_price_history(token_price_history_list)
    db.close()


# we begin to check the xingtai
#     db_folder = '/Users/admin/Desktop/dexprice/MarketSystem/Data/Project'  # 数据库存储文件夹
#     db_name = "chill" + '.db'  # 数据库文件名
  #  chain_id = "solana"
    db = insert_db.SQLiteDatabase(db_folder, db_name, chain_id)
    db.connect()

    tokens = db.readdbtoken()
    requestedtokenid = []
    for token in tokens:
        requestedtokenid.append(token.tokenid)

    db_path = db_folder + '/' + db_name
    task_manager = multidb.DatabaseReadTaskManager(requestedtokenid, db_path, chain_id, max_threads=5)
    results = task_manager.run()
    tokenhistorys = []
    # 处理结果
    for token_id, rows in results:
        tokenhistory = []
        for row in rows:
            test = define.TokenPriceHistory(row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            tokenhistory.append(test)
        tokenhistorys.append(tokenhistory)
    rawdata = tokenhistorys[0]
 #   print(rawdata)
    import importlib
    import dexprice.modules.strategy.normal as normal
    import dexprice.modules.strategy.niuqi as niuqi

    # 对模块重新加载
    importlib.reload(normal)
    dates, opens, highs, lows, closes = normal.checknormalgui(rawdata)
    niu = niuqi.analyze_niuqi_intervals(dates, opens, highs, lows, closes, niuqi.niuqi_interval)

    if (niu == 1):
        print("yes")
    else:
        print("no")

    import dexprice.modules.dearpygui.gui as pygui

    pygui.show_chart_rectangle(dates, opens, highs, lows, closes, niuqi.niuqi_interval)
