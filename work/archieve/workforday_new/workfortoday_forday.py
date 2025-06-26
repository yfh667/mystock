

# 将我们要研究的token存入到today数据库内

import dexprice.modules.PriceMonitor.dexscreen_parrel as dexscreen_parrel
import dexprice.modules.utilis.define as define

#import dexprice.modules.db.insert_db as insert_db
import dexprice.modules.db.insert_db as insert_db

from dexprice.modules.utilis.define import FilterCriteria

import dexprice.modules.db.multidb as multidb

import time
import dexprice.modules.tg.tgbot as tgbot

import dexprice.modules.allmodules.geckpricehistory as geckpricehistory

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


    ## 我们将json的token读取到json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = findroot.find_project_root(current_dir)
    DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")

    # 将我们要研究的token存入到today数据库内
    criteria = FilterCriteria(
        liquidity_usd_min=10000,
        liquidity_usd_max=None,
        fdv_min=100000,
        fdv_max=None,
        pair_age_min_hours=45,
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
    unique_find_address = list(set(find_address))
    for address in unique_find_address:
        print(address)
    db.close()


