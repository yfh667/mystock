import requests

# 统一时间粒度映射 -> Bybit interval


def _convert_interval(interval):
    """统一转换不同接口的时间间隔参数"""

        # 合约接口格式映射
    interval_map = {
        "1M": "1",
        "5M": "5",
        "15M": "15",
        "30M": "30",
        "1H": "60",
        "4H": "240",
        "1D": "D",
        "1W": "W",
        "1MON": "M"
    }
    return interval_map.get(interval, interval)




def get_kline_data(
    symbol: str,
    interval: str = "5M",           # 1M / 5M / 15M / 1H / 4H / 1D …
    start: int | None = None,       # 秒 或 毫秒
    end: int   | None = None,
    port: int = 7890,

):
    """
    返回格式：[[ts, open, high, low, close, volume, turnover], ...]
    """
    category = "linear"     # 线性合约；现货填 spot
    limit = 200                # 1–1000，默认 200
    # Bybit 不接受下划线，统一大写
    symbol = symbol.replace("_", "").upper()

    url = "https://api.bybit.com/v5/market/kline"
    params = {
        "category": category,
        "symbol": symbol,
        "interval": _convert_interval(interval),
        "limit": limit
    }

    # Bybit 要毫秒时间戳；如果给的是秒就 ×1000
    if start is not None:
        params["start"] = start if start > 1e12 else start * 1000
    if end is not None:
        params["end"] = end if end > 1e12 else end * 1000

    proxies = {
        "http":  f"http://127.0.0.1:{port}",
        "https": f"http://127.0.0.1:{port}"
    }

    try:
        response = requests.get(url, params=params, proxies=proxies, timeout=10)
        response.raise_for_status()

        data = response.json()

        ovhl =data["result"]['list']

        return ovhl
        # success_check = lambda data: data.get("code") == 0
        # if success_check(data):
        #
        #     return data
        # else:
        #     error_msg = data.get("msg")
        #     print(f"API Error ({'Contract' }): {error_msg}")

    except requests.exceptions.RequestException as e:
        print(f"Request Failed: {str(e)}")
    except ValueError as e:
        print(f"JSON Parse Error: {str(e)}")

# === 示例 ===
if __name__ == "__main__":
    # klines = get_kline_data(
    #     symbol="BTC_USDT",
    #     interval="1H",
    #     start=1752163200,     # 秒级时间戳 → 会自动转换
    #     end=1752249600,
    #     port=7890
    # )
    klines = get_kline_data("BTC_USDT", '1MON', None, None, 7890)
    print(klines)


  #  kline_data = get_kline_data('BTC_USDT', '1D', 1656604800, 1656777600,7890)



