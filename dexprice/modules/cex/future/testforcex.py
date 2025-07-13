import requests

# 统一时间粒度映射 -> Bybit interval
def cex_test_proxy_port(port: int = 7890,platform='binance'):




    symbol = "BTC_USDT"

    start = 1656604800  # 秒级时间戳 → 会自动转换
    end = 1656777600


    if platform == 'bybit':
        interval = "D"

        category = "linear"  # 线性合约；现货填 spot
        limit = 200  # 1–1000，默认 200
        # Bybit 不接受下划线，统一大写
        symbol = symbol.replace("_", "").upper()

        url = "https://api.bybit.com/v5/market/kline"
        params = {
            "category": category,
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }

        # Bybit 要毫秒时间戳；如果给的是秒就 ×1000
        if start is not None:
            params["start"] = start if start > 1e12 else start * 1000
        if end is not None:
            params["end"] = end if end > 1e12 else end * 1000
        proxies = {
            "http": f"http://127.0.0.1:{port}",
            "https": f"http://127.0.0.1:{port}"
        }
        try:
            response = requests.get(url, params=params, proxies=proxies, timeout=10)
           # response.raise_for_status()  # 检查是否有 HTTP 错误

            # 如果返回的是 403 Forbidden，返回 -1
            if response.status_code == 403:
                print("403 Client Error: Forbidden - IP not supported.")
                return -1
        except requests.exceptions.RequestException as e:
            # 这里捕获请求异常但不返回 -1
            print(f"Request Failed: {str(e)}")
        except ValueError as e:
            # 捕获 JSON 解析错误，但不返回 -1
            print(f"JSON Parse Error: {str(e)}")

        return None  # 如果没有遇到错误或无法获取数据，返回 None


    if platform == 'binance':
        interval = "1d"
        limit = 1500  # 1–1000，现货/合约均可
        category = "futures"  # "futures"（USDT 合约）或 "spot"
        symbol = symbol.replace("_", "").upper()
        # 判断平台的category
        base_url = "https://fapi.binance.com/fapi/v1/klines"
        params = {

            "symbol": symbol,

            "interval": interval,

            "limit": limit

        }

        # Binance 也用毫秒时间戳

        if start is not None:
            params["startTime"] = start if start > 1e12 else start * 1000

        if end is not None:
            params["endTime"] = end if end > 1e12 else end * 1000

        proxies = {

            "http": f"http://127.0.0.1:{port}",

            "https": f"http://127.0.0.1:{port}"

        }

        try:

            response = requests.get(base_url, params=params, proxies=proxies, timeout=10)

            # 如果返回的是 403 Forbidden，返回 -1

            if response.status_code == 451:
                print("403 Client Error: Forbidden - IP not supported.")

                return -1

        except requests.exceptions.RequestException as e:

            # 捕获请求异常

            print(f"Request Failed: {str(e)}")

            return None  # 如果请求失败，返回 None

        except ValueError as e:

            # 捕获 JSON 解析错误

            print(f"JSON Parse Error: {str(e)}")

            return None  # 如果JSON解析失败，返回 None

    return None  # 如果平台不匹配，则返回 None

# === 示例 ===
if __name__ == "__main__":
    klines = cex_test_proxy_port(port=7890,platform='binance')
    print(klines)
