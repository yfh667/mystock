import dexprice.modules.mexc.getalltoken as getalltoken
import dexprice.modules.cexdb.cexdb as cexdb
import time
import dexprice.modules.utilis.define as define
import os
import dexprice.modules.utilis.findroot as findroot
import dexprice.modules.mexc.initial_timesta as initial_timesta
import dexprice.modules.mexc.initial_timesta_parall as initial_timesta_parall
import dexprice.modules.proxy.proxymultitheread as proxymultitheread
import dexprice.modules.mexc.getalltoken as getalltoken
import dexprice.modules.cexdb.cexdb as cexdb
import dexprice.modules.tg.tgbot as tgbot

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
import datetime
import dexprice.modules.cexdb.cexdb as cexdb

import dexprice.modules.utilis.define as define
import os
import dexprice.modules.utilis.findroot as findroot

import  dexprice.modules.cexdb.multidb as multidb

import dexprice.modules.strategy.basefunction as basefunction

def ovhl2_2():
    kline = 'D'
    aggregate = 1

    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = findroot.find_project_root(current_dir)
    DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")

    db_folder = DATA_FOLDER + '/cex'  # 数据库存储文件夹
    db_name_raw = "mexc_contract" + '.db'  # 数据库文件名

    db_mubiao_name = "mexc_contract_wanted_time_price" + str(aggregate) + kline + '.db'
    flag = 1

    db = cexdb.CexSQLiteDatabase(db_folder, db_name_raw)

    db.connect()

    tokens = db.readdbtoken()
    creattime_want = one_geck.datetime_to_timestamp(2020, 1, 1, 0, 0, 0, is_utc=True)

    usetoken = []
    for token in tokens:

        creattime_token = timedefine.datetime_to_timestamp_str(token.creattime)
        if (creattime_token > creattime_want):
            if (token.name.endswith('_USDT')):
                usetoken.append(token)
    print(usetoken)

    db.close()

    # db_mubiao_name = "myspot" + '.db'
    db = cexdb.CexSQLiteDatabase(db_folder, db_mubiao_name)
    db.connect()
    db.insert_Multidata(usetoken)

    price_time_want = one_geck.datetime_to_timestamp(2025, 6, 28, 0, 0, is_utc=True)

    # price_time_want = one_geck.datetime_to_timestamp(2025, 6, 24, 0, 0, 0, is_utc=True)
    # 获取当前时间的 UTC 时间戳
    current_time = datetime.datetime.utcnow()
    current_time = current_time- datetime.timedelta(days=1)
    # 计算前两天的时间

    # current_time = one_geck.datetime_to_timestamp(2025, 7 , 2, 0, 0, is_utc=True)

    two_days_ago = current_time - datetime.timedelta(days=2)

    # 将其转换为时间戳格式
    start_timestamp = two_days_ago.timestamp()

    end_timestamp = one_geck.datetime_to_timestamp(2025, 7, 10, 0, 0, 0, is_utc=True)

    six_day_ago = current_time - datetime.timedelta(days=7)

  #  nowday = current_time - datetime.timedelta(days=1)
    nowday = current_time
    day_ago = nowday - datetime.timedelta(days=7)

    #  start_timestamp = price_time_want
    start_timestamp = day_ago.timestamp()
    # one_day_ago =  current_time - datetime.timedelta(days=2)
    # end_timestamp = timedefine.get_current_utc_timestemp()
    end_timestamp = nowday.timestamp()
    ##
    queues = []

    for token in usetoken:
        queue = mexc_queue.mexc_create_request_queue(token.name, start_timestamp, end_timestamp, kline, aggregate)
        queues.extend(queue)

    rate = 0.3
    capacity = 20
    max_threads_per_proxy = 1
    clash_api_url = "http://127.0.0.1:9097"
    headers = {"Authorization": "Bearer manba"}

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


def ovhl2():
    kline = 'D'
    aggregate = 1

    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = findroot.find_project_root(current_dir)
    DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")

    db_folder = DATA_FOLDER + '/cex'  # 数据库存储文件夹
    db_name_raw = "mexc_contract" + '.db'  # 数据库文件名

    db_mubiao_name = "mexc_contract_wanted_time_price" + str(aggregate) + kline + '.db'
    flag = 1

    db = cexdb.CexSQLiteDatabase(db_folder, db_name_raw)

    db.connect()

    tokens = db.readdbtoken()
    creattime_want = one_geck.datetime_to_timestamp(2020, 1, 1, 0, 0, 0, is_utc=True)

    usetoken = []
    for token in tokens:

        creattime_token = timedefine.datetime_to_timestamp_str(token.creattime)
        if (creattime_token > creattime_want):
            if (token.name.endswith('_USDT')):
                usetoken.append(token)
    print(usetoken)

    db.close()

    # db_mubiao_name = "myspot" + '.db'
    db = cexdb.CexSQLiteDatabase(db_folder, db_mubiao_name)
    db.connect()
    db.insert_Multidata(usetoken)

    price_time_want = one_geck.datetime_to_timestamp(2025, 6, 28, 0, 0, is_utc=True)

    # price_time_want = one_geck.datetime_to_timestamp(2025, 6, 24, 0, 0, 0, is_utc=True)
    # 获取当前时间的 UTC 时间戳
    current_time = datetime.datetime.utcnow()
    # 计算前两天的时间

    # current_time = one_geck.datetime_to_timestamp(2025, 7 , 2, 0, 0, is_utc=True)

    two_days_ago = current_time - datetime.timedelta(days=2)

    # 将其转换为时间戳格式
    start_timestamp = two_days_ago.timestamp()

    end_timestamp = one_geck.datetime_to_timestamp(2025, 7, 10, 0, 0, 0, is_utc=True)

    six_day_ago = current_time - datetime.timedelta(days=7)

  #  nowday = current_time - datetime.timedelta(days=1)
    nowday = current_time
    day_ago = nowday - datetime.timedelta(days=6)

    #  start_timestamp = price_time_want
    start_timestamp = day_ago.timestamp()
    # one_day_ago =  current_time - datetime.timedelta(days=2)
    # end_timestamp = timedefine.get_current_utc_timestemp()
    end_timestamp = nowday.timestamp()
    ##
    queues = []

    for token in usetoken:
        queue = mexc_queue.mexc_create_request_queue(token.name, start_timestamp, end_timestamp, kline, aggregate)
        queues.extend(queue)

    rate = 0.3
    capacity = 20
    max_threads_per_proxy = 1
    clash_api_url = "http://127.0.0.1:9097"
    headers = {"Authorization": "Bearer manba"}

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

def ovhl3():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = findroot.find_project_root(current_dir)
    DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")

    db_folder = DATA_FOLDER + '/cex'  # 数据库存储文件夹
    #   db_name_raw = "mexc_spot" + '.db'  # 数据库文件名
    db_mubiao_name = "mexc_contract_wanted_time_price1D" + '.db'

    db = cexdb.CexSQLiteDatabase(db_folder, db_mubiao_name)

    db.connect()

    tokens = db.readdbtoken()
    requestedtokenid = []
    for token in tokens:
        requestedtokenid.append(token.tokenid)

    db_path = db_folder + '/' + db_mubiao_name

    task_manager = multidb.CexDatabaseReadTaskManager(requestedtokenid, db_path, max_threads=6)
    results = task_manager.run()
    tokenhistorys = []
    # 处理结果
    for token_id, rows in results:
        tokenhistory = []
        for row in rows:
            test = define.CexTokenPriceHistory(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
            tokenhistory.append(test)
        tokenhistorys.append(tokenhistory)

    chat_id = "@jingou26"
    msg_id = 7890
    lines_to_send = []
    lines_to_send.append(f"运行时间: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    lines_to_send.append("高成交量 token：")
    # here is the strategy
    for tokenhistory in tokenhistorys:
        sorthistory = basefunction.sort_by_time(tokenhistory)
        length_his = len(sorthistory)
        # here we could use our strategy .
        if length_his < 7:
            continue
        amount = 0
        counts = 0

        for i in range(length_his - 1):
            amount = amount + sorthistory[i].amount
        avaeg_amoint = amount / (length_his - 1)

        if sorthistory[length_his - 1].amount > 5 * avaeg_amoint:
            token = db.read_token_withid(sorthistory[i].tokenid)
            print("yes", token.name, sorthistory[-1].time)
            lines_to_send.append(token.name)

    # 如果发现有符合的内容才发送
    if len(lines_to_send) :
        message = "\n".join(lines_to_send)
        tgbot.sendmessage_chatid(chat_id, message, msg_id)

    db.close()



    # 构造数据库路径
    db_path_1 = os.path.join(db_folder, "mexc_contract.db")
    db_path_2 = os.path.join(db_folder, "mexc_contract_wanted_time_price1D.db")

    # 安全删除文件（先检查是否存在）
    for path in [db_path_1, db_path_2]:
        if os.path.exists(path):
            os.remove(path)
            print(f"已删除：{path}")
        else:
            print(f"未找到文件：{path}")

def main():


    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = findroot.find_project_root(current_dir)
    DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")

    db_folder = DATA_FOLDER + '/cex'  # 数据库存储文件夹
    db_name = "mexc_contract" + '.db'  # 数据库文件名
    db = cexdb.CexSQLiteDatabase(db_folder, db_name)

    db.connect()

    symbol = getalltoken.getalltoken()
   # symbol  = ['BTC','SOL']
    tokens = []

    rate =0.3
    capacity = 20
    max_threads_per_proxy = 1
    clash_api_url = "http://127.0.0.1:9097"
    headers = {"Authorization": "Bearer manba"}

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

    ovhl2()
    ovhl3()




def main2():


    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = findroot.find_project_root(current_dir)
    DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")

    db_folder = DATA_FOLDER + '/cex'  # 数据库存储文件夹
    db_name = "mexc_contract" + '.db'  # 数据库文件名
    db = cexdb.CexSQLiteDatabase(db_folder, db_name)

    db.connect()

    symbol = getalltoken.getalltoken()
   # symbol  = ['BTC','SOL']
    tokens = []

    rate =0.3
    capacity = 20
    max_threads_per_proxy = 1
    clash_api_url = "http://127.0.0.1:9097"
    headers = {"Authorization": "Bearer manba"}

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

    ovhl2_2()


    ovhl3()


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = findroot.find_project_root(current_dir)
    DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")

    db_folder = DATA_FOLDER + '/cex'  # 数据库存储文件夹
    while True:
        print(f"\n--- 新一轮执行: {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
        main()
        main2()
        print("休眠 8 小时...\n")
        time.sleep(8 * 60 * 60)  # 8 小时