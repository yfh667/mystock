import requests

# 统一时间粒度映射 -> Bybit interval

# 统一粒度 → Binance interval

def _convert_interval(interval):
    """统一转换不同接口的时间间隔参数"""

        # 合约接口格式映射
    interval_map = {
        "1M": "1m",
        "5M": "5m",
        "15M": "15m",
        "30M": "30m",
        "1H": "1h",
        "4H": "4h",
        "1D": "1d",
        "1W": "1w",
        "1MON": "1M"
    }
    return interval_map.get(interval, interval)




def get_kline_data(
    symbol: str,
    interval: str = "5M",           # 5M / 1H / 1D …
    start: int | None = None,       # 秒或毫秒
    end:   int | None = None,
    port:  int = 7890,


):
    """
    返回格式：[[ts, open, high, low, close, volume, ...], ...]
    """
    limit: int = 1500  # 1–1000，现货/合约均可
    category = "futures" # "futures"（USDT 合约）或 "spot"
    symbol = symbol.replace("_", "").upper()

    if category == "spot":
        base_url = "https://api.binance.com/api/v3/klines"
    elif category == "futures":
        base_url = "https://fapi.binance.com/fapi/v1/klines"
    else:
        raise ValueError("category 必须是 'spot' 或 'futures'")

    params = {
        "symbol": symbol,
        "interval": _convert_interval(interval),
        "limit": limit
    }

    # Binance 也用毫秒时间戳
    if start is not None:
        params["startTime"] = start if start > 1e12 else start * 1000
    if end is not None:
        params["endTime"] = end   if end   > 1e12 else end   * 1000

    proxies = {
        "http":  f"http://127.0.0.1:{port}",
        "https": f"http://127.0.0.1:{port}"
    }

    # r = requests.get(base_url, params=params, proxies=proxies, timeout=10)
    # r.raise_for_status()
    # return r.json()        # 直接返回 K 线二维数组
    try:
        response = requests.get(base_url, params=params, proxies=proxies, timeout=10)
        response.raise_for_status()

        data = response.json()
        if  data:

            return data
        else:
            error_msg = data.get("msg")
            print(f"API Error ({'Contract' }): {error_msg}")

    except requests.exceptions.RequestException as e:
        print(f"Request Failed: {str(e)}")
    except ValueError as e:
        print(f"JSON Parse Error: {str(e)}")

    return None
# === 使用示例 ===
if __name__ == "__main__":
    # 拉取 USDT 永续合约 BTC 1H K线
    kl_fut = get_kline_data(
        symbol="BTC_USDT",
        interval="1D",
        start=1656604800,         # 秒 → 自动转毫秒
        end=1656777600,
        port=7890,

    )
    print(kl_fut)

