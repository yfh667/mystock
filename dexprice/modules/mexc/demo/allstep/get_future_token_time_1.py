import dexprice.modules.mexc.getalltoken as getalltoken
import dexprice.modules.cexdb.cexdb as cexdb

import dexprice.modules.utilis.define as define
import os
import dexprice.modules.utilis.findroot as findroot
import dexprice.modules.mexc.initial_timesta as initial_timesta
import dexprice.modules.mexc.initial_timesta_parall as initial_timesta_parall
import dexprice.modules.proxy.proxymultitheread as proxymultitheread

if __name__ == '__main__':


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

    #
    # for symbol in symbol:
    #     token_parts = symbol.split('_')
    #     name = token_parts[0]
    #     chaind = token_parts[1]
    #     time = initial_timesta.determine_initial_timesta(name+'_USDT')
    #     if(time):
    #         creattime= time
    #     else:
    #         creattime=None
    #     token = define.CexTokenInfo(
    #         name=name,  # Token name (string)
    #         chainid=chaind,  # Chain ID (string)
    #         creattime=creattime
    #     )
    #     tokens.append(token)
    # db.insert_Multidata(tokens)
    # # 打印实例属性
    #
    # db.close()