import requests
from datetime import datetime, timezone
import dexprice.modules.utilis.define as define
import requests
import time
from typing import Optional, Dict, Any
import dexprice.modules.proxy.testnetwork as testnetwork
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


#
# def get_ohlcv_data_with_proxy(network: str, pool_address: str, timeframe: str, aggregate: str = "1",
#                               before_timestamp: Optional[str] = None, limit: int = 100,
#                               currency: str = "usd", token: str = "base", proxy_port: Optional[int] = None) -> Optional[Dict[str, Any]]:
#
#     url = f"https://api.geckoterminal.com/api/v2/networks/{network}/pools/{pool_address[0]}/ohlcv/{timeframe}"
#     params = {
#         "aggregate": aggregate,
#         "limit": limit,
#         "currency": currency,
#         "token": token
#     }
#
#     # 添加 before_timestamp 参数，如果存在
#     if before_timestamp:
#         params["before_timestamp"] = before_timestamp
#
#     # 设置代理
#     proxies = None
#     if proxy_port:
#         proxy_url = f"http://127.0.0.1:{proxy_port}"
#         proxies = {
#             'http': proxy_url,
#             'https': proxy_url
#         }
#
#     # 重试设置
#     max_retries = 5
#     retry_count = 0
#
#     # 重试机制
#     while retry_count < max_retries:
#         try:
#             response = requests.get(url, params=params, proxies=proxies, timeout=10)
#             if response.status_code == 200:
#                 return response.json()  # 请求成功返回 JSON 数据
#             elif response.status_code == 429:
#                 print("HTTP 429: Too Many Requests. Retrying after a delay.")
#                 time.sleep(5)  # 等待 5 秒后重试
#             elif response.status_code == 404:
#                 # 如果返回404，直接返回错误
#                 print(f"HTTP 404: Not Found. Returning ERROR.")
#                 # here it implies that it is none
#                 return None
#             else:
#                 print(f"HTTP error: {response.status_code}")
#
#         except requests.RequestException as e:
#             print(f"Request failed: {e}")
#             if(not testnetwork.test_google_through_proxy(proxy_port)):
#                 return None
#
#         retry_count += 1
#         if retry_count < max_retries:
#             print(f"Retrying... ({retry_count}/{max_retries})")
#             time.sleep(2 ** retry_count)  # 指数回退
#
#     print("Max retries reached. Exiting.")
#     return None  # 使用 None 表示请求失败
#
from typing import Optional, Dict, Any
import time
import requests

def get_ohlcv_data_with_proxy(
    network: str,
    pool_address: str,
    timeframe: str,
    aggregate: str = "1",
    before_timestamp: Optional[str] = None,
    limit: int = 100,
    currency: str = "usd",
    token: str = "base",
    proxy_port: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """
    调用 GeckoTerminal DEX API 获取指定池子的 OHLCV 数据（带可选代理与重试机制）。

    参数:
        network (str): 区块链网络 ID（例如 'bsc'）。
        pool_address (str): 池子地址的容器（注意：函数体内使用 pool_address[0]）。
        timeframe (str): 时间粒度 ('day' / 'hour' / 'minute')。
        aggregate (str): 聚合周期（与 timeframe 搭配，如 '5' 表示 5m）。
        before_timestamp (Optional[str]): （可选）在该 Unix 秒级时间戳之前的最近若干根 K 线。
        limit (int): 返回的条数上限。
        currency (str): 计价货币（例如 'usd'）。
        token (str): 价格基准（例如 'base'）。
        proxy_port (Optional[int]): （可选）本地代理端口，如 50005。

    返回:
        Optional[Dict[str, Any]]: 请求成功返回 JSON（dict）；404 或多次失败则返回 None。
    """
    # 构造 URL 与查询参数
    url = f"https://api.geckoterminal.com/api/v2/networks/{network}/pools/{pool_address[0]}/ohlcv/{timeframe}"
    params = {
        "aggregate": aggregate,
        "limit": limit,
        "currency": currency,
        "token": token
    }

    # 可选 before_timestamp
    if before_timestamp:
        params["before_timestamp"] = before_timestamp

    # 可选代理
    proxies = None
    if proxy_port:
        proxy_url = f"http://127.0.0.1:{proxy_port}"
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }

    # 重试配置
    max_retries = 5
    retry_count = 0

    # 重试循环
    while retry_count < max_retries:
        try:
            response = requests.get(url, params=params, proxies=proxies, timeout=10)

            if response.status_code == 200:
                return response.json()  # 请求成功返回 JSON 数据
            elif response.status_code == 429:
                print("HTTP 429: Too Many Requests. Retrying after a delay.")
                time.sleep(5)  # 等待 5 秒后重试
            elif response.status_code == 404:
                # 如果返回404，直接返回错误
                print(f"HTTP 404: Not Found. Returning ERROR.")
                # here it implies that it is none
                return None
            else:
                print(f"HTTP error: {response.status_code}")

        except requests.RequestException as e:
            print(f"Request failed: {e}")
            # 外部网络连通性检测：保持你的原有逻辑
            if (not testnetwork.test_google_through_proxy(proxy_port)):
                return None

        # 指数退避并增加计数
        retry_count += 1
        if retry_count < max_retries:
            print(f"Retrying... ({retry_count}/{max_retries})")
            time.sleep(2 ** retry_count)  # 指数回退

    print("Max retries reached. Exiting.")
    return None  # 使用 None 表示请求失败


def get_ohlcv_data_with_proxy_lite(
    network: str,
    pool_address: str,
    timeframe: str,
    aggregate: str = "1",
    before_timestamp: Optional[str] = None,
    limit: int = 100,
    currency: str = "usd",
    token: str = "base",
    proxy_port: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """
    调用 GeckoTerminal DEX API 获取指定池子的 OHLCV 数据（带可选代理与重试机制）。

    参数:
        network (str): 区块链网络 ID（例如 'bsc'）。
        pool_address (str): 池子地址的容器（注意：函数体内使用 pool_address[0]）。
        timeframe (str): 时间粒度 ('day' / 'hour' / 'minute')。
        aggregate (str): 聚合周期（与 timeframe 搭配，如 '5' 表示 5m）。
        before_timestamp (Optional[str]): （可选）在该 Unix 秒级时间戳之前的最近若干根 K 线。
        limit (int): 返回的条数上限。
        currency (str): 计价货币（例如 'usd'）。
        token (str): 价格基准（例如 'base'）。
        proxy_port (Optional[int]): （可选）本地代理端口，如 50005。

    返回:
        Optional[Dict[str, Any]]: 请求成功返回 JSON（dict）；404 或多次失败则返回 None。
    """
    # 构造 URL 与查询参数
    url = f"https://api.geckoterminal.com/api/v2/networks/{network}/pools/{pool_address[0]}/ohlcv/{timeframe}"
    params = {
        "aggregate": aggregate,
        "limit": limit,
        "currency": currency,
        "token": token
    }

    # 可选 before_timestamp
    if before_timestamp:
        params["before_timestamp"] = before_timestamp

    # 可选代理
    proxies = None
    if proxy_port:
        proxy_url = f"http://127.0.0.1:{proxy_port}"
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }

    # 重试配置
    max_retries = 1
    retry_count = 0

    # 重试循环
    while retry_count < max_retries:
        try:
            response = requests.get(url, params=params, proxies=proxies, timeout=10)

            if response.status_code == 200:
                return response.json()  # 请求成功返回 JSON 数据
            elif response.status_code == 429:
                print("HTTP 429: Too Many Requests. Retrying after a delay.")
                time.sleep(5)  # 等待 5 秒后重试
            elif response.status_code == 404:
                # 如果返回404，直接返回错误
                print(f"HTTP 404: Not Found. Returning ERROR.")
                # here it implies that it is none
                return None
            else:
                print(f"HTTP error: {response.status_code}")

        except requests.RequestException as e:
            print(f"Request failed: {e}")
            # 外部网络连通性检测：保持你的原有逻辑
            if (not testnetwork.test_google_through_proxy(proxy_port)):
                return None

        # 指数退避并增加计数
        retry_count += 1
        if retry_count < max_retries:
            print(f"Retrying... ({retry_count}/{max_retries})")
            time.sleep(2 ** retry_count)  # 指数回退

    print("Max retries reached. Exiting.")
    return None  # 使用 None 表示请求失败


def get_token_history(ohlcv_data, pool_address):
    historydatas = []
    if(ohlcv_data):
        for entry in ohlcv_data['data']['attributes']['ohlcv_list']:

            historydata =  define.OvhlFromDex(pool_address[0],entry[1],entry[2],entry[3],entry[4],timestamp_to_datetime(entry[0]),entry[5])
            # print(entry)
            historydatas.append(historydata)
    return historydatas

def get_token_history2(network: str, pool_address: str, timeframe: str, aggregate: str = "1",
                      before_timestamp: Optional[str] = None, limit: int = 100,
                      currency: str = "usd", token: str = "base", proxy_port: Optional[int] = None) -> Optional[Dict[str, Any]]:
    ohlcv_data = get_ohlcv_data_with_proxy(network, pool_address, timeframe, aggregate, before_timestamp, limit, currency, token, proxy_port)

    historydatas = get_token_history(ohlcv_data, pool_address)
    return historydatas