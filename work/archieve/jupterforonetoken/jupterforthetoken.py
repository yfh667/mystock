
import  dexprice.modules.utilis.define as define

import dexprice.modules.db.insert_db as insert_db

import dexprice.modules.db.multidb as multidb

def find_all_stable_ranges(dates, opens, highs, lows, closes, daily_threshold=0.5, range_threshold=1):
    """
    寻找所有平稳区间，并返回包含所有区间的列表。
    每个区间的波动范围要求在 threshold 以内。

    平稳区间定义：
    - 至少包含两天（两个及以上的数据点）。
    - 每天的波动幅度 (high - low) / open 不超过 daily_threshold。
    - 区间内收盘价的波动幅度 (max(close) - min(close)) / min(close) 不超过 range_threshold。

    参数：
    - dates: 时间戳或日期列表（与价格数据对应）
    - opens: 开盘价列表
    - highs: 最高价列表
    - lows: 最低价列表
    - closes: 收盘价列表
    - daily_threshold: 每日波动阈值（默认0.5，即50%）
    - range_threshold: 区间内收盘价波动阈值（默认0.5，即50%）

    返回：
    - stable_intervals: list of tuples
      每个元素为 (x_start, x_end, y_start, y_end)
      表示一个平稳区间的起止时间和最低/最高价格范围。
    """
    stable_intervals = []
    n = len(dates)
    start = 0

    while start < n:
        end = start
        # 尝试扩展区间
        while end < n:
            # 检查每日波动幅度
            fluctuation = (highs[end] - lows[end]) / opens[end]
            if abs(fluctuation) > daily_threshold:
                break
            end += 1

        # end是第一个超出阈值的位置或已到结尾
        if end - start > 1:
            # 检查区间内的收盘价波动幅度
            close_min = min(closes[start:end])
            close_max = max(closes[start:end])
            close_range = (close_max - close_min) / close_min

            if  close_range  <= range_threshold:
                # 找到一个平稳区间
                y_min = min(lows[start:end])
                y_max = max(highs[start:end])
                x_start = dates[start]
                x_end = dates[end - 1]
                stable_intervals.append((x_start, x_end, y_min, y_max))

            # 无论是否满足收盘价波动范围，从end位置继续寻找下一个区间
            start = end
        else:
            # 当前区间长度 <= 1，不算平稳区间，从下一个位置继续
            start += 1 if end == start else end - start

    return stable_intervals
## use postql, we could neleget it
if __name__ == "__main__":



    chain_id = "solana"
    db_folder = '/Users/admin/Desktop/dexprice/MarketSystem/Data/Project'   # 数据库存储文件夹
    db_name = "evan"+'.db'  # 数据库文件名
    db = insert_db.SQLiteDatabase(db_folder, db_name,chain_id)
    db.connect()

    tokens = db.readdbtoken()
    requestedtokenid = []
    for token in tokens:
        requestedtokenid.append(token.tokenid)

    db_path = db_folder+'/'+db_name
    task_manager = multidb.DatabaseReadTaskManager(requestedtokenid,  db_path,chain_id, max_threads=6)
    results = task_manager.run()
    tokenhistorys = []
    # 处理结果
    for token_id, rows in results:
        tokenhistory=[]
        for row in rows:
            test = define.TokenPriceHistory(row[1],row[2],row[3],row[4],row[5],row[6],row[7])
            tokenhistory.append(test)
        tokenhistorys.append(tokenhistory)

    rawdata = tokenhistorys[0]
    import dexprice.modules.utilis.timedefine as transtime
    # 初始化空列表
    dates = []
    opens = []
    highs = []
    lows = []
    closes = []
    for record in rawdata:
        timestamp = transtime.datetime_to_timestamp(record.time)  # 转换时间为时间戳
        dates.append(timestamp)
        opens.append(record.open)
        highs.append(record.high)
        lows.append(record.low)
        closes.append(record.close)
    import  dexprice.modules.dearpygui.gui as  pygui

    stable_intervals = find_all_stable_ranges(dates, opens, highs, lows, closes, daily_threshold=0.5,range_threshold=1)
    pygui.show_chart_rectangle(dates,opens,highs,lows,closes,find_all_stable_ranges)