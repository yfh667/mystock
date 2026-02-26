import time
from datetime import datetime, timedelta, timezone

import dexprice.modules.biance.cex_queue as cex_queue


import dexprice.modules.biance.ovhl_binance as ovhl_binance


import dexprice.modules.biance.cex_basic_ovhl as cex_basic_ovhl


##---下面是两种方式获取
# 直接以藏柜的symbol 时间范围的方式获取
def biance_token_history(symbol, interval="Min15", start=None, end=None,port=7890 ,limit=1500,category='futures',cexname = 'binance'):
    kline_data = ovhl_binance.get_kline_data(symbol, interval, start, end,port,limit,category)
    historydatas = cex_basic_ovhl.biance_token_history_basic(kline_data, symbol,cexname)
    return historydatas

# 以queue的方式进行
def biance_token_history_use_queue(  queue: cex_queue.CexKlineQueue,port=7890 ,limit=1500,category='futures',cexname = 'binance'):
    symbol = queue.symbol
    kline = queue.kline
    aggregate = queue.aggregate
    starttime = queue.starttime
    endtime = queue.endtime
    interval  =str(aggregate)+ str(kline)
    kline_data = ovhl_binance.get_kline_data(symbol, interval, int(starttime), int(endtime),port,limit,category)
    historydatas = cex_basic_ovhl.biance_token_history_basic(kline_data, symbol,cexname)
    return historydatas

#
if __name__ == "__main__":

# we test the biance_token_history
        print("=== 开始测试 biance_token_history 获取历史 K 线 ===")

        # 1. 准备测试参数
        test_symbol = "BTC_USDT"  # 测试币种
        test_interval = "1H"  # 测试时间级别：1小时线
        test_category = "futures"  # 测试合约数据

        # 设置拉取时间：获取过去 3 天到昨天的数据
        now = datetime.now(timezone.utc)
        end_dt = now - timedelta(days=1)
        start_dt = end_dt - timedelta(days=3)

        test_start = int(start_dt.timestamp())
        test_end = int(end_dt.timestamp())

        print(f"请求参数: Symbol={test_symbol}, Interval={test_interval}")
        print(f"时间范围: {start_dt.strftime('%Y-%m-%d %H:%M:%S')} 到 {end_dt.strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 2. 调用函数
        try:
            history_data = biance_token_history(
                symbol=test_symbol,
                interval=test_interval,
                start=test_start,
                end=test_end,
                port=7890,  # 确保你的代理端口没变
                limit=1500,
                category=test_category,
                cexname='binance'  # 对应你 flag 的逻辑，如果之前 flag!=1 是走 else 分支，这里要注意匹配
            )

            # 3. 验证并打印结果
            if not history_data:
                print("⚠️ 未获取到数据，请检查网络/代理，或确认该时间段内是否有 K 线。")
            else:
                print(f"✅ 成功获取到 {len(history_data)} 根 K 线数据！\n")

                # 打印第一根和最后一根数据，检查解析对象是否正确
                print("【第一条数据】:")
                print(f"  时间: {history_data[0].time}")
                print(
                    f"  开/高/低/收: {history_data[0].open} / {history_data[0].high} / {history_data[0].low} / {history_data[0].close}")
                print(f"  成交量: {history_data[0].volume}\n")

                print("【最后一条数据】:")
                print(f"  时间: {history_data[-1].time}")
                print(
                    f"  开/高/低/收: {history_data[-1].open} / {history_data[-1].high} / {history_data[-1].low} / {history_data[-1].close}")
                print(f"  成交量: {history_data[-1].volume}")

        except Exception as e:
            print(f"❌ 测试运行出错: {e}")