import requests

def bitget_history_mark_kline(
    symbol: str,
    granularity: str = "5m",          # 1m / 5m / 15m / 1H / 4H / 1D ...
    product_type: str = "USDT-FUTURES",
    start_time: int | None = None,    # 毫秒时间戳，可留空
    end_time: int | None = None,      # 毫秒时间戳，可留空
    limit: int = 100                  # 1‒200
):
    """
    返回格式：[[ts, open, high, low, close, baseVol, quoteVol], ...]
    """
    url = "https://api.bitget.com/api/v2/mix/market/history-candles"
    params = {
        "symbol": symbol,
        "granularity": granularity,
        "productType": product_type,
        "limit": limit,
    }
    if start_time:
        params["startTime"] = start_time
    if end_time:
        params["endTime"] = end_time

    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    if data.get("code") == "00000":
        return data["data"]          # K 线列表
    else:
        raise RuntimeError(f"API error: {data}")

# === 示例 ===
if __name__ == "__main__":



    klines = bitget_history_mark_kline(
        symbol="BTCUSDT",
        granularity="1H",
        limit=50
    )
    print(f"拿到 {len(klines)} 根 5 分钟 K 线")
    print(klines[-1])                # 打印前 3 根
