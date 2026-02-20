
import  dexprice.modules.OHLCV.geck as geck
import time
from datetime import  timezone

import datetime

import time
from datetime import datetime, timedelta
def timestamp_to_datetime(timestamp, to_utc=True):
    """
    将时间戳转换为日期时间格式。

    参数:
    - timestamp: 时间戳（秒）
    - to_utc: 是否返回 UTC 时间

    返回:
    - 日期时间格式
    """
    if to_utc:
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)
    else:
        return datetime.fromtimestamp(timestamp)

if __name__ == "__main__":
    # 示例用法
    network = "bsc"
    pool_address = ['0x7F0B9A92fe7ABBC64d38cbD02a3c39191657b8bB']
    timeframe = "day"  # 可选值: day, hour, minute





    aggregate = "1"     # 聚合时间段


    # 当前时间戳
    current_timestamp = int(time.time())

    # 转换成 datetime 对象（UTC）
    current_dt = datetime.fromtimestamp(current_timestamp, tz=timezone.utc)

    # 150 天前
    day_ago_dt = current_dt - timedelta(days=10)

    # 转回时间戳
    before_timestamp =1755431848



    limit = 100
    currency = "usd"
    token = "base"
    proxy_port = 7890  # 指定代理端口

    ohlcv_data = geck.get_token_history2(network, pool_address, timeframe, aggregate, before_timestamp, limit, currency, token, proxy_port)


    for data in ohlcv_data:
        print(data.time)
    # print(ohlcv_data[0])



# Out[1]: 'bsc'
# pool_address
# Out[2]: ['0x7F0B9A92fe7ABBC64d38cbD02a3c39191657b8bB']
# timeframe
# Out[3]: 'day'
# aggregate
# Out[4]: '1'
# before_timestamp
# Out[5]: 1755431848
# limit
# Out[6]: 100
# currency
# Out[7]: 'usd'
