import dexprice.modules.cex.future.cex_getall_token_future as getalltoken



import dexprice.modules.cexdb.cexdb as cexdb

import dexprice.modules.utilis.define as define
import os
import dexprice.modules.utilis.findroot as findroot
import dexprice.modules.mexc.initial_timesta as initial_timesta
import dexprice.modules.cex.future.cex_ovhl as initial_timesta_parall
import dexprice.modules.proxy.proxymultitheread as proxymultitheread
import dexprice.modules.cex.future.starttime_bybit as starttime_bybit
import dexprice.modules.cex.future.starttime_binance as starttime_binance

import dexprice.modules.cex.future.starttime_bitget as starttime_bitget

import dexprice.modules.cex.future.testforcex as testforcex

import dexprice.modules.cex.cex_proxy as cex_proxy
if __name__ == '__main__':


    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = findroot.find_project_root(current_dir)
    DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")


    db_folder = DATA_FOLDER + '/cex'  # 数据库存储文件夹
    rate = 0.3
    capacity = 20
    max_threads_per_proxy = 1
    clash_api_url = "http://127.0.0.1:9097"
    headers = {"Authorization": "Bearer manba"}

    startport = 50000




    cex_name = 'binance'
    db_name = cex_name+"_contract" + '.db'  # 数据库文件名
    db = cexdb.CexSQLiteDatabase(db_folder, db_name)

    db.connect()

    symbol = getalltoken.get_all_token(cex_name, 7890)
   # symbol  = ['BTC','SOL']




    proxys = cex_proxy.get_one_ip_proxy_multithread_distinct(startport, clash_api_url, headers,cex_name)

    task_manager = initial_timesta_parall.CexTaskManager(
        symbol,
        proxys,
        rate,
        capacity,
        max_threads_per_proxy,
        starttime_binance.determine_initial_timesta

    )
    results, failed_tasks = task_manager.run()
    db.insert_Multidata(results)
    # 打印实例属性
    db.close()




    cex_name = 'bybit'
    db_name = cex_name + "_contract" + '.db'  # 数据库文件名
    db = cexdb.CexSQLiteDatabase(db_folder, db_name)

    db.connect()

    symbol = getalltoken.get_all_token(cex_name, 7890)
    # symbol  = ['BTC','SOL']


    proxys = cex_proxy.get_one_ip_proxy_multithread_distinct(startport, clash_api_url, headers, cex_name)

    task_manager = initial_timesta_parall.CexTaskManager(
        symbol,
        proxys,
        rate,
        capacity,
        max_threads_per_proxy,
        starttime_bybit.determine_initial_timesta

    )
    results, failed_tasks = task_manager.run()
    db.insert_Multidata(results)
    # 打印实例属性
    db.close()

    cex_name = 'bitget'
    db_name = cex_name + "_contract" + '.db'  # 数据库文件名
    db = cexdb.CexSQLiteDatabase(db_folder, db_name)

    db.connect()

    symbol = getalltoken.get_all_token(cex_name, 7890)
    # symbol  = ['BTC','SOL']

    proxys = cex_proxy.get_one_ip_proxy_multithread_distinct(startport, clash_api_url, headers, cex_name)

    task_manager = initial_timesta_parall.CexTaskManager(
        symbol,
        proxys,
        rate,
        capacity,
        max_threads_per_proxy,
        starttime_bitget.determine_initial_timesta

    )
    results, failed_tasks = task_manager.run()
    db.insert_Multidata(results)
    # 打印实例属性
    db.close()