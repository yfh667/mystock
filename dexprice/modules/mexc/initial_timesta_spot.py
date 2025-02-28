import requests
import json
import time
import time
import dexprice.modules.utilis.timedefine as timedefine
def get_kline_data(symbol, interval="1M", start=None, end=None,port=7890):
  #  url = f"https://api.mexc.com/api/v3/klines?symbol={symbol}"
    #params = {"interval": interval}
    url = "https://api.mexc.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,

    }

    # if start_time and end_time:
    #     params["startTime"] = start_time
    #     params["endTime"] = end_time
    #
    # response = requests.get(url, params=params)

    if start:
        params["startTime"] = start
    if end:
        params["endTime"] = end
    httpurl = "http://127.0.0.1:"+str(port)

    proxies = {
        "http": httpurl,
        "https": httpurl
    }

    # 生成完整 URL 并打印
   # full_url = requests.Request('GET', url, params=params).prepare().url
  #  print(f"Request URL: {full_url}")

    response = requests.get(url, params=params,proxies=proxies)


 #   response = requests.get(url, params=params)

    if response.status_code == 200:
            data = response.json()

            if len(data) > 0:
                return data
            else:
                print("API Response Error:", data)
                print(f"the token is {symbol}")
    else:
            print("HTTP Request Failed with Status Code:", response.status_code)

            return None



def determine_initial_timesta(symbol,port=7890):
    interval = "1M"
    start = None  # 允许为空
    # end is the now time
   # end = 1738308461  # 允许为空
    end = None
   # end = int(time.time())
    kline_data = get_kline_data(symbol, interval, start, end,port)
    times = []
    for d in kline_data:
        time = d[0]
        times.append(time)
   # time = kline_data['time']
    if (len(times) <= 1000):
        start = times[0]
        #here we find the start month
        #and we need find the start time
        # end = timedefine.mexc_addtime(start/1000) *1000
        interval = '1d'
        # kline_data = get_kline_data(symbol, interval, start, end,port)
        #
        # real_start = kline_data[0][0]
      #  time  = timedefine.timestamp_to_datetime(start //1000)

        start ,end=  timedefine.mexc_addtime(start //1000)
        kline_data = get_kline_data(symbol, interval, start, end, port)
        time  = kline_data[0][0]
        strtime = timedefine.timestamp_to_datetime(time //1000)

        return strtime
    else:
        # we need tiqian 1nian

    #    start = times[0]






        print(" to old we  delete")
        return None




# 我找到规律了，就是这样的，我的start一定要大于end一个interval，比如，start是12号，intervl是1d，那么end必须是13号，至于几点无所谓

#
# start =1483228800000
# end =1546300800000
# kline_data = get_kline_data('SNTUSDT', '1d', start, end, 7890)
# print(kline_data)
# TIME =  determine_initial_timesta('SNTUSDT',port=7890)
# print(TIME)
