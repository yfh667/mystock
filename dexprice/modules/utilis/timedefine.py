from datetime import datetime, timedelta
from datetime import datetime, timezone
import time


def get_current_utc_timestemp():
    """
    获取当前UTC日期并返回格式为 '2024-09-13' 的字符串
    """

    current_utc_time =int(time.time())
    return current_utc_time

# print(get_current_utc())
def get_current_utc_date():
    """
    获取当前UTC日期并返回格式为 '2024-09-13' 的字符串
    """
    current_utc_time = datetime.utcnow()
    formatted_date = current_utc_time.strftime('%Y-%m-%d')
    return formatted_date

def get_past_utc_date(days_in_past):
    """
    获取过去指定天数的UTC日期并返回格式为 '2024-09-13' 的字符串
    :param days_in_past: 距离当前的天数
    """
    current_utc_time = datetime.utcnow()
    past_utc_time = current_utc_time - timedelta(days=days_in_past)
    formatted_date = past_utc_time.strftime('%Y-%m-%d')
    return formatted_date

def compare_utc_dates(utc_date1, utc_date2):
    """
    比较两个UTC日期，返回较早的日期
    :param utc_date1: 第一个UTC日期的字符串，格式为'%Y-%m-%d'
    :param utc_date2: 第二个UTC日期的字符串，格式为'%Y-%m-%d'
    :return: 返回较早的UTC日期
    """
    # 将日期字符串解析为 datetime 对象
    date1 = datetime.strptime(utc_date1, '%Y-%m-%d')
    if " " in utc_date2:  # 判断是否包含时间部分
        utc_date2 = utc_date2.split(" ")[0]

    date2 = datetime.strptime(utc_date2, '%Y-%m-%d')

    # 比较两个日期，返回较早的日期
    if date1 < date2:
        return 1  # date1 较早
    elif date1 > date2:
        return 0  # date2 较早
    else:
        return 1  # 日期相同

def format_date(datetime_str):
    """将日期时间字符串格式化为仅包含日期的字符串"""
    date_only = datetime_str.split(' ')[0]
    return date_only
#
# # 示例
# datetime_input = '2024-09-24 10:50:38'
# date_only = remove_time(datetime_input)
# print(date_only)  # 输出：2024-09-24
#

def timestamp_to_datetime(timestamp, to_utc=True):
    """
    将时间戳转换为日期时间格式。

    参数:
    - timestamp: 时间戳（秒）
    - to_utc: 是否返回 UTC 时间

    返回:
    - 日期时间格式
    """
    if to_utc:
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)
    else:
        return datetime.fromtimestamp(timestamp)


# import time
#
# current_timestamp = int(time.time())
# print(current_timestamp)


def datetime_to_timestamp(dt, is_utc=True):
    """
    将 datetime 对象转换为时间戳。

    参数:
    - dt: datetime 对象
    - is_utc: 是否为 UTC 时间

    返回:
    - 时间戳（秒）
    """
    if is_utc:
        return int(dt.replace(tzinfo=timezone.utc).timestamp())
    else:
        return int(dt.timestamp())


def compare(creattime, now):
    """
    比较 creattime 和 now 是否在同一个小时内。

    参数:
    - creattime: 创建时间（字符串格式：%Y-%m-%d %H:%M:%S）
    - now: 当前时间（字符串格式：%Y-%m-%d %H:%M:%S）

    返回:
    - 1: 如果 creattime 和 now 在同一个小时内
    - 0: 否则
    """
    # 将 creattime 和 now 转为 datetime 对象
    dt_creattime = datetime.strptime(creattime, "%Y-%m-%d %H:%M:%S")
    dt_now = datetime.strptime(now, "%Y-%m-%d %H:%M:%S")

    # 比较年月日和小时
    if dt_creattime.year == dt_now.year and \
            dt_creattime.month == dt_now.month and \
            dt_creattime.day == dt_now.day and \
            dt_creattime.hour == dt_now.hour:
        return 1  # 同一小时内
    else:
        return 0  # 不在同一小时内
# t2 = '2024-11-17 06:01:06'
# t1 = '2024-11-17 06:59:06'
# print(compare(t1, t2))


def klinetime(creatime, klinetime):
    """
    判断 klinetime 是否晚于 creatime 1 小时。

    参数:
    - creatime: 创建时间（字符串格式：%Y-%m-%d %H:%M:%S）
    - klinetime: 比较时间（字符串格式：%Y-%m-%d %H:%M:%S）

    返回:
    - True: 如果 klinetime 晚于 creatime 1 小时
    - False: 如果 klinetime 不满足条件
    """
    # 将 creatime 和 klinetime 转为 datetime 对象
    dt_creatime = datetime.strptime(creatime, "%Y-%m-%d %H:%M:%S")
    dt_klinetime = datetime.strptime(klinetime, "%Y-%m-%d %H:%M:%S")

    # 判断 klinetime 是否比 creatime 晚 1 小时
    if dt_klinetime >= dt_creatime + timedelta(hours=1):
        return True
    else:
        return False

# # 测试
# creatime1 = '2024-11-17 06:01:06'
# klinetime1 = '2024-11-17 06:05:06'
# print(klinetime(creatime1, klinetime1))  # 输出 False
#
# creatime2 = '2024-11-17 08:00:12'
# klinetime2 = '2024-11-17 10:00:00'
# print(klinetime(creatime2, klinetime2))  # 输出 True


def timestamp_to_datetime(timestamp, to_utc=True):
    """
    将时间戳转换为日期时间格式。

    参数:
    - timestamp: 时间戳（秒）
    - to_utc: 是否返回 UTC 时间

    返回:
    - 日期时间格式字符串，如 "2024-04-27 18:47:09"
    """
    if to_utc:
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    else:
        dt = datetime.fromtimestamp(timestamp)

    # 格式化为 "YYYY-MM-DD HH:MM:SS" 形式
    return dt.strftime("%Y-%m-%d %H:%M:%S")
# print(timestamp_to_datetime(1733561645))

import time

def datetime_to_timestamp_str(date_time_str):
    """
    Convert a datetime string to a timestamp.

    Args:
        date_time_str (str): The datetime string in the format 'YYYY-MM-DD HH:MM:SS'.

    Returns:
        int: The corresponding timestamp in seconds.
    """
    try:
        # Parse the datetime string to a datetime object
        dt = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
        # Convert datetime object to timestamp
        timestamp = int(time.mktime(dt.timetuple()))
        return timestamp
    except ValueError as e:
        print(f"Error: {e}")
        return None

# # Example usage
# date_time_str = "2024-1-31 00:00:00"
# timestamp = datetime_to_timestamp(date_time_str)
# print(f"The timestamp for  '{date_time_str}' is: {timestamp}")

#获得当前时间的标准k线起始时间，
#例如，2024-09-02:36:00 的标准k线起始时间是 2024-09-02:00:00
#2024-12-24 19:58:16



from datetime import datetime

def get_the_utc_1h(date_time_str):
    """
    将给定的时间字符串转换为每小时整点的标准K线起始时间。

    参数:
    date_time_str (str): 输入的时间字符串，例如 "2024-12-24 19:58:16"

    返回:
    str: 每小时的标准K线起始时间，例如 "2024-12-24 19:00:00"
    """
    # 将输入的时间字符串解析为 datetime 对象
    dt = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
    # 替换分钟和秒为 0，获取整点时间
    kline_start_time = dt.replace(minute=0, second=0, microsecond=0)
    # 返回整点时间的字符串格式
    return kline_start_time.strftime("%Y-%m-%d %H:%M:%S")

# # 测试用例
# example_time = "2024-12-24 18:58:16"
# result = get_the_utc_1h(example_time)
# print(result)  # 输出: "2024-12-24 19:00:00"


# 我们获得后面一个月的第一天。
#如果当前是12月，那么就是第二年的一月第一天
def addtime(starttime):
    formatted_date = timestamp_to_datetime(starttime)
  #  formatted_date = starttime.strftime('%Y-%m-%d')
    dt = datetime.strptime(formatted_date, "%Y-%m-%d %H:%M:%S")
    month = dt.month
    year = dt.year

    if month>=11:
        endtime = dt.replace(year=year+1,day=1,month=1, minute=0, second=0, microsecond=0)
    else:
        endtime = dt.replace(month=month+2,day=1,minute=0, second=0, microsecond=0)


    # if month == 12:
    #     endtime = dt.replace(year=year+1,day=1,month=1, minute=0, second=0, microsecond=0)
    # else:
    #
    #     endtime = dt.replace(month=month+2,day=1,minute=0, second=0, microsecond=0)
    end_string = endtime.strftime("%Y-%m-%d %H:%M:%S")
   # end_utc = datetime.strptime(end_string, "%Y-%m-%d %H:%M:%S")
    end_utc =  datetime_to_timestamp_str(end_string)
    return end_utc

def mexc_addtime(starttime):
    formatted_date = timestamp_to_datetime(starttime)
  #  formatted_date = starttime.strftime('%Y-%m-%d')
    dt = datetime.strptime(formatted_date, "%Y-%m-%d %H:%M:%S")
   # month = dt.month
    year = dt.year

    # start = dt.replace(year=year,day=1,month=1, minute=0, second=0, microsecond=0)
    # end = dt.replace(year=year+1,day=1,month=1, minute=0, second=0, microsecond=0)
    # from datetime import datetime

    # year = 2024
    # dt = datetime.now()

    # 设定 start 为当年1月1日 00:00:00
    start = dt.replace(year=year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    # 设定 end 为下一年1月1日 00:00:00
    end = dt.replace(year=year + 2, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    # print("Start:", start)
    # print("End:", end)

   #  # if month == 12:
   #  #     endtime = dt.replace(year=year+1,day=10,month=1, minute=0, second=0, microsecond=0)
   #  # else:
   #  #
   #  #     endtime = dt.replace(month=month+1,day=10,minute=0, second=0, microsecond=0)
   #  # end_string = endtime.strftime("%Y-%m-%d %H:%M:%S")
   # # end_utc = datetime.strptime(end_string, "%Y-%m-%d %H:%M:%S")
   #  end_utc =  datetime_to_timestamp(end_string)
   # start_string = start.strftime("%Y-%m-%d %H:%M:%S")
    #start_dt = datetime.strptime(start_string, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)

    start_utc = datetime_to_timestamp(start)
    end_utc = datetime_to_timestamp(end)
    # end_string = end.strftime("%Y-%m-%d %H:%M:%S")
    # end_utc = datetime_to_timestamp(end_string,is_utc=True)

    return 1000*start_utc ,1000*end_utc
# starttime = 1733299200
# end =addtime(starttime)
# print(end)



