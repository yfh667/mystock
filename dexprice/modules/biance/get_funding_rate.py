import requests
from datetime import datetime, timezone


def get_binance_funding_rate(
        symbol: str,
        start: int | None = None,  # 秒或毫秒时间戳
        end: int | None = None,  # 秒或毫秒时间戳
        limit: int = 1000,  # biance最大 1000
        port: int = 7890
) -> list[dict] | None:
    """
    获取币安 USDT 本位合约的历史资金费率。

    返回数据格式示例:
    [
        {
            "symbol": "BTCUSDT",
            "fundingRate": "0.00010000",
            "fundingTime": 1570622400000
        },
        ...
    ]
    """
    # 格式化 symbol
    symbol = symbol.replace("_", "").upper()

    base_url = "https://fapi.binance.com/fapi/v1/fundingRate"

    params = {
        "symbol": symbol,
        "limit": limit
    }

    # 时间戳处理：币安要求毫秒
    if start is not None:
        params["startTime"] = start if start > 1e12 else int(start * 1000)
    if end is not None:
        params["endTime"] = end if end > 1e12 else int(end * 1000)

    # 代理设置，规避 451 地区限制错误
    proxies = {
        "http": f"http://127.0.0.1:{port}",
        "https": f"http://127.0.0.1:{port}"
    }

    try:
        response = requests.get(base_url, params=params, proxies=proxies, timeout=10)
        response.raise_for_status()

        data = response.json()
        if data:
            return data
        else:
            print("API 返回为空或没有符合条件的数据。")
            return []

    except requests.exceptions.HTTPError as e:
        # 尝试捕获币安返回的具体错误信息
        try:
            error_msg = response.json().get("msg")
            print(f"API Error: {error_msg}")
        except ValueError:
            pass
        print(f"HTTP Request Failed: {str(e)}")
    except requests.exceptions.RequestException as e:
        print(f"Request Failed: {str(e)}")
    except ValueError as e:
        print(f"JSON Parse Error: {str(e)}")

    return None


# === 测试代码 ===
if __name__ == "__main__":
    print("=== 开始获取 Binance 历史资金费率 ===")

    test_symbol = "BTCUSDT"

    # 设定时间范围：比如 2024年1月1日 到 2024年1月10日
    start_dt = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end_dt = datetime(2024, 1, 10, tzinfo=timezone.utc)

    start_ts = int(start_dt.timestamp())
    end_ts = int(end_dt.timestamp())

    print(f"请求币种: {test_symbol}")
    print(f"时间范围: {start_dt.strftime('%Y-%m-%d')} 到 {end_dt.strftime('%Y-%m-%d')}\n")

    funding_rates = get_binance_funding_rate(
        symbol=test_symbol,
        start=start_ts,
        end=end_ts,
        limit=1000,
        port=7890
    )

    if funding_rates:
        print(f"✅ 成功获取到 {len(funding_rates)} 条资金费率记录！\n")

        # 打印头尾两条数据做验证
        first_record = funding_rates[0]
        last_record = funding_rates[-1]

        # 将毫秒时间戳转为人类可读时间
        first_time = datetime.fromtimestamp(first_record['fundingTime'] / 1000, tz=timezone.utc).strftime(
            '%Y-%m-%d %H:%M:%S')
        last_time = datetime.fromtimestamp(last_record['fundingTime'] / 1000, tz=timezone.utc).strftime(
            '%Y-%m-%d %H:%M:%S')

        print("【最早的一条记录】:")
        print(f"  时间: {first_time} (UTC)")
        print(f"  费率: {float(first_record['fundingRate']) * 100:.4f} %")

        print("\n【最晚的一条记录】:")
        print(f"  时间: {last_time} (UTC)")
        print(f"  费率: {float(last_record['fundingRate']) * 100:.4f} %")