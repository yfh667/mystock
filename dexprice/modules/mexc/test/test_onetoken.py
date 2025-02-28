import requests
import json
import time
import time
import dexprice.modules.utilis.timedefine as timedefine
import dexprice.modules.OHLCV.one_geck as one_geck

import dexprice.modules.mexc.mexc_queue as mexc_queue

symbol= 'PEP1_USDT'
# 生成开始和结束时间的时间戳
start_timestamp = one_geck.datetime_to_timestamp(2025, 2, 20, 0, 0, 0, is_utc=True)
end_timestamp = one_geck.datetime_to_timestamp(2025, 2, 23, 0, 0, 0, is_utc=True)
kline = 'D'
aggregate = '1'



queue = mexc_queue.mexc_create_request_queue(symbol, start_timestamp, end_timestamp, kline, aggregate)
print(queue)






# print(queue)
# print(queue[0].pool_addresses)
#
clash_api_url = "http://127.0.0.1:9097"
headers = {"Authorization": "Bearer 123"}

startport = 50000
proxys = []
proxysport =clash.get_one_ip_proxy(startport,clash_api_url,headers)

# 添加代理到代理池
for port in proxysport:
    socksproxy = '127.0.0.1:' + str(port)
    ip = testproxy.fetch_public_ip_via_http_proxy(socksproxy)
    if ip !=None:
        proxy = proxydefine.Proxy(port, ip)
        proxys.append(proxy)

rate =0.5
capacity = 30
chain_id = 'solana'

max_threads_per_proxy = 1
#  proxy = proxydefine.Proxy(port=50008, ip='127.0.0.1')
# proxys =  []
# proxys.append(proxy)
task_manager = geck_parrel2.GeckTaskManager2(queue,  chain_id, proxys, rate, capacity, max_threads_per_proxy)
results, failed_tasks = task_manager.run()
for result in results:
    print(result)