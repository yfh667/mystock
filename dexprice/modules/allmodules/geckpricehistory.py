import dexprice.modules.db.insert_db as insert_db
import dexprice.modules.OHLCV.geck_parrel as geck_parrel
import math
import time
# Define a function to try deleting the table with retry logic
import dexprice.modules.proxy.proxymultitheread as proxymultitheread
import dexprice.modules.allmodules.geckpricehistory as geckpricehistory
def get_interval_seconds(timeframe, aggregate):
    aggregate = int(aggregate)  # 将 aggregate 转换为整数

    if timeframe == 'day':
        interval_seconds = 24 * 3600 * aggregate
    elif timeframe == 'hour':
        interval_seconds = 3600 * aggregate
    elif timeframe == 'minute':
        interval_seconds = 60 * aggregate
    else:
        raise ValueError("Invalid timeframe")
    return interval_seconds

def get_total_points(times, interval_seconds):
    total_seconds = times * 3600
    total_points = math.ceil(total_seconds / interval_seconds)
    return total_points

def get_number_of_calls(total_points, limit):
    number_of_calls = math.ceil(total_points / limit)
    return number_of_calls

def get_times_before(times, timeframe, aggregate, limit):
    interval_seconds = get_interval_seconds(timeframe, aggregate)
    total_points = get_total_points(times, interval_seconds)
    number_of_calls = get_number_of_calls(total_points, limit)

    calls = []
    current_timestamp = int(time.time())

    for i in range(number_of_calls):
        if i < number_of_calls - 1:
            call_limit = limit
        else:
            remaining_points = total_points - limit * (number_of_calls - 1)
            call_limit = int(remaining_points)
            # 为了保险，多获取一个数据点
            call_limit += 1

        before_timestamp = current_timestamp - interval_seconds * limit * i
        calls.append({'before_timestamp': before_timestamp, 'limit': call_limit})

    return calls
def gethistorywithgeck(realpairaddress,chain_id,proxys,timeframe,aggregate,before_timestamp,limit):
    rate = 0.4
    capacity =30
    max_threads_per_proxy =1

    task_manager = geck_parrel.GeckTaskManager(
        realpairaddress,
        chain_id,
        proxys,
        rate,
        capacity,
        max_threads_per_proxy,
        timeframe,
        aggregate,
        before_timestamp,
        limit
    )
    results, failed_tasks = task_manager.run()
    return results


def inserthistorywithgeck_db(db:insert_db.SQLiteDatabase,realpairaddress,chain_id,proxys,timeframe,aggregate,before_timestamp,limit):
    results = gethistorywithgeck(realpairaddress,chain_id,proxys,timeframe,aggregate,before_timestamp,limit)
    token_price_history_list = db.collect_ovhl_data(results)
    # 批量插入数据
    db.insert_multiple_price_history(token_price_history_list)



def inserthistorywithgeck_db2(db, realpairaddress, chain_id, proxys, timeframe, aggregate, times, limit=100):
    calls = get_times_before(times, timeframe, aggregate, limit)
    for call in calls:
        before_timestamp = call['before_timestamp']
        call_limit = call['limit']
        # 获取历史数据
        inserthistorywithgeck_db(db,realpairaddress,chain_id,proxys,timeframe,aggregate,before_timestamp,call_limit)


def inserthistoryforaddress(db:insert_db.SQLiteDatabase,tokendata,timeframe,aggregate,before_timestamp,geck_limit):
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
  #  current_timestamp = int(time.time())
 #   before_timestamp = str(current_timestamp)  # 当前时间的时间戳
    clash_api_url = "http://127.0.0.1:9097"
    headers = {"Authorization": "Bearer 123"}
    startport = 50000
    for chain, pairaddresses in chain_addresses.items():
        proxys = proxymultitheread.get_one_ip_proxy_multithread(startport, clash_api_url, headers)
        if chain == "ethereum":
            chainid = 'eth'
        else:
            chainid = chain
        print(f"we check Chain: {chain} ")
        inserthistorywithgeck_db(db, pairaddresses, chainid, proxys, timeframe,
                                                  aggregate, before_timestamp, geck_limit)
