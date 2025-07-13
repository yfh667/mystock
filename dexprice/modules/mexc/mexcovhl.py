import requests
import json
import time
import time
import dexprice.modules.utilis.timedefine as timedefine
import dexprice.modules.mexc.mexc_queue as mexc_queue
import dexprice.modules.utilis.define as define
#flag =0 :spot 1:contract

def _convert_interval(interval, flag):
    """统一转换不同接口的时间间隔参数"""
    if flag == 1:
        # 合约接口格式映射
        interval_map = {
            "1M": "Min1",
            "5M": "Min5",
            "15M": "Min15",
            "30M": "Min30",
            "1H": "Min60",
            "4H": "Hour4",
            "1D": "Day1",
            "1W": "Week1",
            "1MON": "Month1"
        }
        return interval_map.get(interval, interval)
    else:

        interval_map = {
            "1M": "1m",
            "5M": "5m",
            "15M": "15m",
            "30M": "30m",
            "1H": "60m",
            "4H": "4h",
            "1D": "1d",
            "1W": "1W",
            "1Mon": "1M"
        }
        return interval_map.get(interval, interval)

def get_kline_data(symbol, interval="15M", start=None, end=None, port=7890, flag=1):
    """
    获取 MEXC K线数据（兼容合约和现货接口）

    :param symbol: 交易对符号 (如 BTC_USDT)
    :param interval: K线间隔（不同接口格式不同）
    :param start: 起始时间戳（秒/毫秒根据接口自动处理）
    :param end: 结束时间戳
    :param port: 代理端口
    :param flag: 1=合约接口 2=现货接口
    :return: 标准化的K线数据列表
    """
    # 接口配置
    if flag == 1:
        # 合约接口参数
        url = "https://contract.mexc.com/api/v1/contract/kline/" + symbol
        time_param_map = {"start": "start", "end": "end"}  # 合约接口使用秒级时间戳
        success_check = lambda data: data.get("code") == 0
        data_extractor = lambda data: data.get("data", [])
    else:
        # 现货接口参数
        url = "https://api.mexc.com/api/v3/klines"
        time_param_map = {"start": "startTime", "end": "endTime"}  # 现货接口使用毫秒级时间戳
        success_check = lambda data: isinstance(data, list)  # 现货直接返回数组
        data_extractor = lambda data: data

    # 参数处理
    params = {"interval": _convert_interval(interval, flag)}

    # 时间戳处理（合约用秒，现货用毫秒）
    if start:
        params[time_param_map["start"]] = start * (1000 if flag != 1 else 1)
    if end:
        params[time_param_map["end"]] = end * (1000 if flag != 1 else 1)

    if flag != 1:
        params["symbol"] = symbol.replace("_", "")  # 现货接口格式：BTCUSDT

    # 代理配置
    proxies = {"http": f"http://127.0.0.1:{port}", "https": f"http://127.0.0.1:{port}"}

    try:
        response = requests.get(url, params=params, proxies=proxies, timeout=10)
        response.raise_for_status()

        data = response.json()

        if success_check(data):

            return data
        else:
            error_msg = data.get("msg") if flag == 1 else "Invalid response structure"
            print(f"API Error ({'Contract' if flag == 1 else 'Spot'}): {error_msg}")

    except requests.exceptions.RequestException as e:
        print(f"Request Failed: {str(e)}")
    except ValueError as e:
        print(f"JSON Parse Error: {str(e)}")

    return None


def mexc_token_history(ohlcv_data, pool_address):
    historydatas = []
    if(ohlcv_data):
        for entry in ohlcv_data['data']['attributes']['ohlcv_list']:
            pass
           # historydata =  define.OvhlFromCex(pool_address[0],entry[1],entry[2],entry[3],entry[4],timestamp_to_datetime(entry[0]),entry[5])
            # print(entry)
            #historydatas.append(historydata)
    return historydatas



def determine_initial_timesta(symbol,port=7890):
    interval = "Month1"
    start = None  # 允许为空
    # end is the now time
   # end = 1738308461  # 允许为空
    end = None
   # end = int(time.time())
    kline_data = get_kline_data(symbol, interval, start, end,port)
    time = kline_data['time']
    if (len(time) <= 2000):
        start = time[0]
        #here we find the start month
        #and we need find the start time
        end = timedefine.addtime(start)
        interval = 'Day1'
        kline_data = get_kline_data(symbol, interval, start, end,port)
        real_start = kline_data['time'][0]
        time  = timedefine.timestamp_to_datetime(real_start)
        return time
    else:
        print(" to old we  delete")
        return None


def mexc_token_history_basic(ohlcv_data, symbol,flag=1):
    historydatas = []

    if flag == 1:
        ohlcv_data = ohlcv_data["data"]
        timelen = len(ohlcv_data.get('time'))

        if(timelen ==0):
            return []
        if(ohlcv_data):
            for i in range(timelen):
                timedata = ohlcv_data.get('time')[i]
                open = ohlcv_data.get('open')[i]
                high = ohlcv_data.get('high')[i]
                low = ohlcv_data.get('low')[i]
                close = ohlcv_data.get('close')[i]
                volume = ohlcv_data.get('vol')[i]
                amount = ohlcv_data.get('amount')[i]
                historydata =  define.OvhlFromCex(symbol,open,high,low,close,timedefine.timestamp_to_datetime(timedata),volume,amount)

                historydatas.append(historydata)
        return historydatas
    else:
        if(not ohlcv_data):
            #here sometime the token is not in the cex,so it is ignored
            return []
        timelen =len(ohlcv_data)
        if (timelen == 0):
            return []
        for i in range(timelen):
            dataovhl = ohlcv_data[i]
            timedata = dataovhl[0] /1000
            open = dataovhl[1]
            high = dataovhl[2]
            low = dataovhl[3]
            close = dataovhl[4]
            volume =dataovhl[5]
            amount = dataovhl[7]
            historydata = define.OvhlFromCex(symbol, open, high, low, close, timedefine.timestamp_to_datetime(timedata),
                                             volume, amount)

            historydatas.append(historydata)
        return historydatas



def mexc_token_history(symbol, interval="Min15", start=None, end=None,port=7890 ,flag =1):
    kline_data = get_kline_data(symbol, interval, start, end,port,flag)
    historydatas = mexc_token_history_basic(kline_data, symbol,flag)
    return historydatas


def mexc_token_history_queue(  queue: mexc_queue.mexcqueue,port=7890 ,flag=1):
    symbol = queue.symbol
    kline = queue.kline
    aggregate = queue.aggregate
    starttime = queue.starttime
    endtime = queue.endtime
    interval  =str(aggregate)+ str(kline)
    kline_data = get_kline_data(symbol, interval, int(starttime), int(endtime),port,flag)
    historydatas = mexc_token_history_basic(kline_data, symbol,flag)
    return historydatas

#
if __name__ == "__main__":

    kline_data = get_kline_data('RFC_USDT', '1D', 1743462796, 1743505996,7890,0)

    print(kline_data)