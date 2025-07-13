# 示例调用
import dexprice.modules.mexc.initial_timesta as initial_timesta
if __name__ == "__main__":
    symbol = "DOODIUSDT"
    # interval = "Month1"
    # start = None  # 允许为空
    # end = 1738308461  # 允许为空
    #
    # kline_data = get_kline_data(symbol, interval, start, end)
    # time = kline_data['time']
    # if(len(time)  <=2000):
    #     start = time[0]
    # if kline_data:
    #     print(json.dumps(kline_data, indent=4))
    time = initial_timesta.determine_initial_timesta(symbol,55511)
    if(time):
        print(time)