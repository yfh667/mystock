from datetime import datetime, timezone
from datetime import datetime, timedelta, timezone
import math
import dexprice.modules.OHLCV.one_geck as one_geck
from dateutil.relativedelta import relativedelta
class CexKlineQueue:
    def __init__(self, symbol, kline:str, aggregate:str, starttime:int,endtime:int,  ):
        """
        初始化请求参数类的实例。

         :param kline: str, K线类型（'minute', 'hour', 'day'）。
        :param aggregate: str, 聚合时间段（例如 '1', '5', '15'）。
        :param before_timestamp: str, 请求之前的时间戳（UTC Unix 时间戳）。
        :param limit: int, 返回的最大数据条数。
          """
        self.symbol = symbol
        self.kline = kline
        self.aggregate = aggregate
        self.starttime = starttime
        self.endtime = endtime


    def __repr__(self):
        """
        定义对象的字符串表示。
        """
        return f"addressesqueue(symbol={self.symbol}, kline={self.kline}, aggregate={self.aggregate}, starttime={self.starttime}, endtime={self.endtime})"

    def to_tuple(self):
        """
        转换实例为元组形式。
        :return: tuple, 包含实例所有属性的元组。
        """
        return (self.symbol, self.kline, self.aggregate, self.starttime, self.endtime,
            )


from datetime import datetime, timedelta


def ceil_timestamp(timestamp: datetime, kline: str, aggregate: int) -> datetime:
    if kline == 'M':
        total_minutes = timestamp.hour * 60 + timestamp.minute
        remainder = total_minutes % aggregate

        if remainder == 0 and timestamp.second == 0 and timestamp.microsecond == 0:
            return timestamp

        add_minutes = aggregate - remainder if remainder != 0 else 0
        new_time = (timestamp + timedelta(minutes=add_minutes)).replace(
            second=0, microsecond=0
        )
        return new_time

    elif kline == 'H':
        remainder = timestamp.hour % aggregate
        # 检查是否已经是周期整点（分钟、秒、微秒全为0）
        if remainder == 0 and timestamp.minute == 0 and timestamp.second == 0 and timestamp.microsecond == 0:
            return timestamp

        # 计算需要增加的小时数
        if remainder != 0:
            add_hours = aggregate - remainder
        else:
            add_hours = aggregate  # 余数为0但时间不在整点，需加一个完整周期

        new_hour = timestamp.hour + add_hours
        days = new_hour // 24
        new_hour = new_hour % 24

        new_time = timestamp.replace(
            hour=new_hour, minute=0, second=0, microsecond=0
        ) + timedelta(days=days)
        return new_time

    elif kline == 'D':
        if timestamp.hour == 0 and timestamp.minute == 0 and timestamp.second == 0 and timestamp.microsecond == 0:
            return timestamp

        return (timestamp + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    elif kline == 'W':
        days_to_add = (7 - timestamp.weekday()) % 7
        # 如果已经是周一0点且时间正确
        if days_to_add == 0 and timestamp.time() == datetime.min.time():
            return timestamp

        # 如果是周一但时间不为0点，仍然需要加7天
        if days_to_add == 0:
            days_to_add = 7

        return (timestamp.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=days_to_add))
    elif kline == 'Mon':
        if timestamp.day == 1 and timestamp.time() == datetime.min.time():
            return timestamp

        # 计算下个月首日
        year = timestamp.year + (timestamp.month // 12)
        month = timestamp.month % 12 + 1
        try:
            # 修改点：加上 tzinfo=timestamp.tzinfo
            return datetime(year, month, 1, tzinfo=timestamp.tzinfo)
        except ValueError:  # 处理12月+1的情况
            # 修改点：加上 tzinfo=timestamp.tzinfo
            return datetime(year + 1, 1, 1, tzinfo=timestamp.tzinfo)

    # elif kline == 'Mon':
    #     if timestamp.day == 1 and timestamp.time() == datetime.min.time():
    #         return timestamp
    #
    #     # 计算下个月首日
    #     year = timestamp.year + (timestamp.month // 12)
    #     month = timestamp.month % 12 + 1
    #     try:
    #         return datetime(year, month, 1)
    #     except ValueError:  # 处理12月+1的情况（会变成13，需转为下一年1月）
    #         return datetime(year + 1, 1, 1)

    else:
        raise ValueError(f"Invalid kline type: {kline}")


def cexkline_create_request_queue(symbol: str,
                         start_timestamp: int,
                         end_timestamp: int,
                         kline: str,
                         aggregate: str,
max_limit:int,
                             ) -> list[tuple]:
    """
    创建一个请求队列，用于获取指定时间戳范围内的 k 线数据。

    队列中的每个元素都是一个元组：
    (pool_address, kline, aggregate, before_timestamp, limit, currency, token)

    参数:
        symbol : 代币符号。
        start_timestamp (int): 开始时间的 Unix 时间戳（秒）。
        end_timestamp (int): 结束时间的 Unix 时间戳（秒）。
        kline (str): K 线类型（'day'、'hour' 或 'minute'）。
        aggregate (str): 聚合间隔（'1'、'5'、'15'、'4'、'12'）。
        max_limit : 交易所的限制，。biance：1500


    返回:
        List[Tuple]: 每个请求批次的参数元组列表。
    """
    # 验证时间戳
    if end_timestamp <= start_timestamp:
        raise ValueError("结束时间戳必须大于开始时间戳。")


    # 根据 kline 和 aggregate 定义每个 k 线的持续时间
    try:
        agg = int(aggregate)
    except ValueError:
        raise ValueError(f"聚合值必须是整数，收到的值：{aggregate}")

    # 将时间戳转换为 datetime 对象
    start_dt = datetime.fromtimestamp(start_timestamp, tz=timezone.utc)
    end_dt = datetime.fromtimestamp(end_timestamp, tz=timezone.utc)

    start_dt = ceil_timestamp(start_dt, kline, agg)
    end_dt=ceil_timestamp(end_dt, kline, agg)

    if kline == 'Mon':
        months_diff = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month)
        total_k_lines = int(math.ceil(months_diff / agg))
        total_k_lines = max(1, total_k_lines)
    else:
        if kline == 'M':
            kline_duration = timedelta(minutes=agg)
        elif kline == 'H':
            kline_duration = timedelta(hours=agg)
        elif kline == 'D':
            kline_duration = timedelta(days=agg)
        elif kline == 'W':
            kline_duration = timedelta(weeks=agg)
        else:
            raise ValueError(f"无效的 kline 值：{kline}")

        kline_seconds = kline_duration.total_seconds()
        total_seconds = (end_dt - start_dt).total_seconds()
        total_k_lines = int(math.ceil(total_seconds / kline_seconds))



    # 初始化请求队列
    request_queue = []

    # 每次请求的最大限制
    # max_limit = 2000

    # 从结束时间开始向前迭代
    current_endtime = end_dt

    while total_k_lines > 0:
        # 确定当前批次的 limit
        limit = min(max_limit, total_k_lines)

        # before_timestamp 是当前结束时间的 Unix 时间戳
        before_timestamp = str(int(current_endtime.timestamp()))



        # 更新 total_k_lines 和 current_endtime 以进行下一次迭代
        total_k_lines -= limit

        if kline == 'Mon':
            # 使用 relativedelta 完美处理跨月，自动处理月末天数问题
            current_endtime -= relativedelta(months=agg * limit)
        else:
            # 其他周期继续使用 timedelta
            time_delta = kline_duration * limit
            current_endtime -= time_delta

        # # 将 current_endtime 向前移动 (limit * kline_duration)
        # time_delta = kline_duration * limit
        # current_endtime -= time_delta

        request_queue.append(CexKlineQueue(
            symbol=symbol,
            kline=kline,
            aggregate=aggregate,
            starttime=str(int(current_endtime.timestamp())),
            endtime=before_timestamp,


        ))
        # 确保不会早于 start_dt
        if current_endtime <= start_dt:
            break

    return request_queue


if __name__ == '__main__':
    # 1. 准备单币种测试参数
    symbol = "BTC_USDT"
    kline = "H"  # 测试逻辑
    aggregate = "4"  # 4h
    max_limit = 1500  # 假设交易所单次最多只给 5 根月线，测试我们的分批逻辑

    # 假设开始时间是 2023年1月15日，结束时间是 2024年3月10日
    # (这正好能测试我们的 ceil_timestamp 向上取整逻辑)
    start_dt = datetime(2023, 1, 15, tzinfo=timezone.utc)
    end_dt = datetime(2024, 3, 10, tzinfo=timezone.utc)

    start_timestamp = int(start_dt.timestamp())
    end_timestamp = int(end_dt.timestamp())

    print(f"请求区间: {start_dt}  -->  {end_dt}\n")

    # 2. 调用生成队列函数
    try:
        queues = []
        # 参考你提供的格式，这里只对单个 symbol 操作
        queue = cexkline_create_request_queue(
            symbol=symbol,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            kline=kline,
            aggregate=aggregate,
            max_limit=max_limit
        )
        queues.extend(queue)

        # 3. 打印结果，直观查看时间分批是否正确
        print(f"成功生成！总共分成了 {len(queues)} 个请求批次：\n")

        for i, q in enumerate(queues):
            # 将时间戳转回人类可读的时间字符串，方便检查
            start_str = datetime.fromtimestamp(int(q.starttime), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            end_str = datetime.fromtimestamp(int(q.endtime), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

            print(f"=== 批次 {i + 1} ===")
            print(f"  Symbol: {q.symbol}")
            print(f"  时间段: {start_str}  -->  {end_str}")
            print(f"  类对象: {q}")

    except Exception as e:
        print(f"💥 运行出错了: {e}")


