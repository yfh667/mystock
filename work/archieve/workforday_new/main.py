import dexprice.modules.utilis.define as define
import dexprice.modules.allmodules.geckpricehistory as geckpricehistory

import dexprice.modules.db.insert_db as insert_db

from dexprice.modules.utilis.define import FilterCriteria

import dexprice.modules.db.multidb as multidb

import time
import dexprice.modules.tg.tgbot as tgbot
# Define a function to try deleting the table with retry logic
import dexprice.modules.proxy.proxymultitheread as proxymultitheread

import os
import dexprice.modules.utilis.findroot as findroot
import dexprice.modules.allmodules.refreshmaindb as refreshmaindb

def pingwen(tokenhistorys: list[define.TokenPriceHistory]):
    #  print(tokenhistorys)
    open = tokenhistorys[0].open
    last = tokenhistorys[-1].close
    if(len(tokenhistorys)>5):
        if last > 0.8 * open:
            return True


def try_delete_table_with_retry(db, retries=3, delay=5):
    for attempt in range(retries):
        try:
            db.delete_table2()
            print("Table deleted successfully.")
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached. Could not delete table.")
                return False


if __name__ == "__main__":

    import dexprice.modules.allmodules.initialtoken as initialtoken


    ## 我们将json的token读取到json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = findroot.find_project_root(current_dir)
    DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")
    filepath  = DATA_FOLDER+'/result.json'
    initialtoken.initialtoken3(filepath)
    refreshmaindb.refreshmaindb()

    # 将我们要研究的token存入到today数据库内
    criteria = FilterCriteria(
        liquidity_usd_min=10000,
        liquidity_usd_max=None,
        fdv_min=100000,
        fdv_max=None,
        pair_age_min_hours=1,
        pair_age_max_hours=24,
        txn_buy=10,
        txn_sell=10,
        volume=10000
    )
    db_name = 'today'
    import dexprice.modules.allmodules.project as project
    from dexprice.modules.utilis.define import FilterCriteria

    project.setproject(db_name, criteria)

    ##读取today里的token
    clash_api_url = "http://127.0.0.1:9097"
    headers = {"Authorization": "Bearer 123"}

    db_folder = DATA_FOLDER + '/Project'  # 数据库存储文件夹

    db = insert_db.SQLiteDatabase(db_folder, db_name + '.db')
    db.connect()

    geck_rate = 0.4
    geck_capacity = 24
    timeframe = "hour"  # 可选值: day, hour, minute
    aggregate = "1"  # 聚合时间段 5min k-line
    geck_limit = 30  # 我们检查5-10h之内的，因此limit提高到了10h。
    geck_max_threads_per_proxy = 1
    dex_rate = 5
    dex_capacity = 300
    dex_max_threads_per_proxy = 3

    sourcetype = define.Config.DEXS

    tokendata = db.readdbtoken()

    # 初始化字典，用链名作为键，地址列表作为值
    chain_addresses = {
        'solana': [],
        'base': [],
        'ethereum': [],
        'bsc': []
    }

    # 遍历 token_new，根据链名将地址加入对应的列表
    for token in tokendata:
        # 确保 token.chainid 是链名，并存在于字典的键中
        if token.chainid in chain_addresses:
            chain_addresses[token.chainid].append(token.pair_address)  # 添加地址到对应链的列表

    current_timestamp = int(time.time())
    before_timestamp = str(current_timestamp)  # 当前时间的时间戳

    for chain, pairaddresses in chain_addresses.items():
        print(f"we check Chain: {chain} ")
        sourcetype = define.Config.DEXS
        max_threads_per_proxy = 2
        clash_api_url = "http://127.0.0.1:9097"
        headers = {"Authorization": "Bearer 123"}
        startport = 50000
        proxys = proxymultitheread.get_one_ip_proxy_multithread(startport, clash_api_url, headers)
        if chain == "ethereum":
            chainid = 'eth'
        else:
            chainid = chain
        geckpricehistory.inserthistorywithgeck_db(db, pairaddresses, chainid, proxys, timeframe,
                                                  aggregate, before_timestamp, geck_limit)

    tokens = db.readdbtoken()
    ## 读取token的历史数据，进行处理
    db_path = db_folder + '/' + db_name + '.db'
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

    find_address = []
    for tokenhistory in tokenhistorys:

        if (len(tokenhistory) > 1):
            if tokenhistory[-1].close > 0.8 * tokenhistory[0].open:
                for i in range(1, len(tokenhistory)):
                    #     for token in tokenhistory:
                    token = tokenhistory[i]
                    if (token.high > 5 * token.low):
                        # 我么需要判断是涨还是跌
                        if (token.close > token.open):
                            tokenid = tokenhistory[0].tokenid
                            tokendb = db.read_token_withid(tokenid)
                            pairaddress = tokendb.pair_address
                            find_address.append(pairaddress)
                    #  print(pairaddress)

    # 输出前的去重操作。
    unique_find_address = list(set(find_address))

    db.close()


    criteria = FilterCriteria(
        liquidity_usd_min=10000,
        liquidity_usd_max=None,
        fdv_min=100000,
        fdv_max=None,
        pair_age_min_hours=24,
        pair_age_max_hours= None,
        txn_buy=50,
        txn_sell=50,
        volume=1000

    )
    db_name = 'thistoday'
    import dexprice.modules.allmodules.project as project
    from dexprice.modules.utilis.define import FilterCriteria

    project.setproject( db_name, criteria)

    ##读取today里的token
    clash_api_url = "http://127.0.0.1:9097"
    headers = {"Authorization": "Bearer 123"}


    db_folder = DATA_FOLDER + '/Project'  # 数据库存储文件夹

    db = insert_db.SQLiteDatabase(db_folder, db_name + '.db')
    db.connect()

    geck_rate = 0.4
    geck_capacity = 24
    timeframe = "day"  # 可选值: day, hour, minute
    aggregate = "1"  # 聚合时间段 5min k-line
    geck_limit = 100  # 我们检查5-10h之内的，因此limit提高到了10h。
    geck_max_threads_per_proxy = 1
    dex_rate = 5
    dex_capacity = 300
    dex_max_threads_per_proxy = 3

    sourcetype = define.Config.DEXS

    tokendata = db.readdbtoken()


    current_timestamp = int(time.time())
    before_timestamp = str(current_timestamp)  # 当前时间的时间戳

    geckpricehistory.inserthistoryforaddress(db, tokendata, timeframe, aggregate, before_timestamp, geck_limit)

    tokens = db.readdbtoken()
    ## 读取token的历史数据，进行处理
    db_path = db_folder + '/' + db_name + '.db'

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

    find_address = []
    for tokenhistory in tokenhistorys:
        if (len(tokenhistory) > 1):
                    token = tokenhistory[-1]
                    if (token.high > 5 * token.low):
                        # 我么需要判断是涨还是跌
                        if (token.close > token.open):
                            tokenid = tokenhistory[0].tokenid
                            tokendb = db.read_token_withid(tokenid)
                            pairaddress = tokendb.pair_address
                            find_address.append(pairaddress)

    # 输出前的去重操作。
    unique_find_address2 = list(set(find_address))
    alllist = unique_find_address+unique_find_address2
    unique_all = list(set(alllist))
    for address in unique_all:
        print(address)
    db.close()





