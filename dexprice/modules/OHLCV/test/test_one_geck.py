
import  dexprice.modules.OHLCV.geck as geck

import dexprice.modules.OHLCV.one_geck as one_geck
pool_address = ['uZAxBqsQokCvnEdUo6hd21QRRYbp2jaXuGDYmHFZgAF']

# 生成开始和结束时间的时间戳
# 注意了，测试的时候，这个时间要在当前时间半年内的
start_timestamp = one_geck.datetime_to_timestamp(2026, 1, 25, 7, 40, 0, is_utc=True)
end_timestamp = one_geck.datetime_to_timestamp(2026, 1, 25, 9, 5, 0, is_utc=True)



kline = 'minute'
aggregate = '5'
currency = "usd"
token = 'base'
proxy_port = 7890  # 指定代理端口
queue = one_geck.create_request_queue(pool_address, start_timestamp, end_timestamp, kline, aggregate)

ohlcv_data = geck.get_token_history2("solana", queue[0].pool_address, kline, aggregate, queue[0].before_timestamp, queue[0].limit, currency, token, proxy_port)

# ohlcv_data2 = geck.get_token_history2("solana", pool_address, kline, aggregate, queue[1][3], queue[1][4], currency, token, proxy_port)
# print(ohlcv_data2)
for params in queue:
    print(params)

print(ohlcv_data)
# 创建 RequestParams 实例
