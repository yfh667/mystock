
import  dexprice.modules.utilis.define as define
import dexprice.modules.db.insert_db as insert_db

import dexprice.modules.PriceMonitor.dexscreen_priceapi as dexscreen_priceapi

import dexprice.modules.OHLCV.one_geck as one_geck
import dexprice.modules.OHLCV.geck_parrel2 as geck_parrel2
import dexprice.modules.proxy.proxymultitheread as proxymultitheread
import os
import dexprice.modules.utilis.findroot as findroot
## use postql, we could neleget it
if __name__ == "__main__":

    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = findroot.find_project_root(current_dir)
    DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")
    db_folder = DATA_FOLDER + '/Project'  # 数据库存储文件夹

    db_name = "chill"+'.db'  # 数据库文件名
    db = insert_db.SQLiteDatabase(db_folder, db_name)
    db.connect()

    address = ['8C6PLY2viiVwFb1QRBnWiQHbVhrn62Z5H2HecGrNwCt6']
    proxy_port = 50000
    chain_id = "solana"
    tokeninfo = dexscreen_priceapi.Get_Token_Dexscreen(define.Config.DEXS,chain_id,address, proxy_port)
    tokeninfos = []
    tokeninfos.extend(tokeninfo)
    db.insert_multiple_tokeninfo(tokeninfos)
    tokensdata = db.readdbtoken()
    paireaddress = []
    for token in tokensdata:
        paireaddress.append(token.pair_address)
    print(paireaddress)

    pool_address = paireaddress
    # 生成开始和结束时间的时间戳
    start_timestamp = one_geck.datetime_to_timestamp(2025, 1, 26, 5, 45, 0, is_utc=True)
    end_timestamp = one_geck.datetime_to_timestamp(2025, 1, 26, 6, 55, 0, is_utc=True)
    kline = 'minute'
    aggregate = '5'
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
    # for result in results:
    #     print(result)
    token_price_history_list = db.collect_ovhl_data(results)
    # 批量插入数据
    db.insert_multiple_price_history(token_price_history_list)
    db.close()