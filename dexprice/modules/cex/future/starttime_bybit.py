

import dexprice.modules.cex.future.ovhl_bybit as ovhl_bybit
import dexprice.modules.utilis.timedefine as timedefine

def determine_initial_timesta(symbol,port=7890):
    interval = "1MON"
    start = None  # 允许为空
    # end is the now time
   # end = 1738308461  # 允许为空
    end = None
   # end = int(time.time())
    kline_data = ovhl_bybit.get_kline_data(symbol, interval, start, end,port)
    time = []
    for i in kline_data:
        time.append(i[0])


    if (len(time) <= 2000):
        start = int(time[-1])//1000
        #here we find the start month
        #and we need find the start time
        end = timedefine.addtime(start)
        interval = '1D'
        kline_data = ovhl_bybit.get_kline_data(symbol, interval, start, end,port)
        real_start = int(kline_data[-1][0])//1000
        time  = timedefine.timestamp_to_datetime(real_start)
        return time
    else:
        print(" to old we  delete")
        return None


if __name__ == "__main__":
    symbol = "BTC_USDT"
    time = determine_initial_timesta(symbol,7890)
    if(time):
        print(time)