

import dexprice.modules.cex.future.ovhl_bitget as ovhl_bitget
import dexprice.modules.utilis.timedefine as timedefine

def determine_initial_timesta(symbol,port=7890):
    interval = "1MON"
    start = None  # 允许为空
    # end is the now time
   # end = 1738308461  # 允许为空
    end = None
   # end = int(time.time())
    kline_data = ovhl_bitget.get_kline_data(symbol, interval, start, end,port)

    if len(kline_data) ==0:
        kline_data = ovhl_bitget.get_kline_data(symbol,  '1W', start, end, port)


    time = []

    for i in kline_data:
        time.append(i[0])

    if (len(time) <= 2000):
        start = int(time[0])//1000
        #here we find the start month
        #and we need find the start time
        end = timedefine.addtime(start)
        interval = '1D'
        kline_data = ovhl_bitget.get_kline_data(symbol, interval, start, end,port)
        real_start = int(kline_data[0][0])//1000
        time  = timedefine.timestamp_to_datetime(real_start)
        return time
    else:
        print(" to old we  delete")
        return None


if __name__ == "__main__":
    symbol = "CBK_USDT"
    time = determine_initial_timesta(symbol,7890)
    if(time):
        print(time)