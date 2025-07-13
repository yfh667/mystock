import requests

def _convert_interval(interval):
    """统一转换不同接口的时间间隔参数"""

        # 合约接口格式映射
    interval_map = {
        "1M": "1m",
        "5M": "5m",
        "15M": "15m",
        "30M": "30m",
        "1H": "1H",
        "4H": "4H",
        "1D": "1D",
        "1W": "1W",
        "1MON": "1M"
    }
    return interval_map.get(interval, interval)


def get_kline_data(
    symbol: str,
    interval: str = "5M",          # 1m / 5m / 15m / 1H / 4H / 1D ...

    start: int | None = None,    # 毫秒时间戳，可留空
    end: int | None = None,      # 毫秒时间戳，可留空
    port=7890
):
    """
    返回格式：[[ts, open, high, low, close, baseVol, quoteVol], ...]
    """
    limit: int = 200                  # 1‒200
    product_type: str = "USDT-FUTURES",
    symbol = symbol.replace("_", "").upper()

    url = "https://api.bitget.com/api/v2/mix/market/history-candles"
    granularity = _convert_interval(interval)

    params = {
        "symbol": symbol,
        "granularity": granularity,
        "productType": product_type,
        "limit": limit,
    }
    # Bitget 要毫秒；如果你给的是秒就 ×1000
    if start is not None:
        params["startTime"] = start if start > 1e12 else start * 1000
    if end is not None:
        params["endTime"] = end if end > 1e12 else end * 1000

    proxies = {"http": f"http://127.0.0.1:{port}", "https": f"http://127.0.0.1:{port}"}


    r = requests.get(url, params=params,proxies=proxies, timeout=10)
    r.raise_for_status()
    data = r.json()

    if data.get("code") == "00000":
        return data["data"]          # K 线列表
    else:
        raise RuntimeError(f"API error: {data}")


if __name__ == "__main__":

    kline_data = get_kline_data('BTC_USDT', '1D', 1656604800, 1656777600,7890)

    print(kline_data)