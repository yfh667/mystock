
import os
import os
import requests
from typing import List, Dict

import os
import sys
import csv
import requests
def _fetch_bitget(proxies: Dict, product_type: str = "USDT-FUTURES") -> List[Dict]:
    endpoint = "https://api.bitget.com/api/v2/mix/market/tickers"
    params = {"productType": product_type}
    try:
        r = requests.get(endpoint, params=params, proxies=proxies, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data.get("code") != "00000":
            print("Bitget error:", data.get("msg"))
            return []
        return data.get("data", [])
    except requests.RequestException as e:
        print("Bitget fetch error:", e)
        return []
def _fetch_bybit(proxies: Dict, limit: int = 1000) -> List[Dict]:
    endpoint = "https://api.bybit.com/v5/market/instruments-info"
    params = {"category": "linear", "limit": limit}
    instruments: List[Dict] = []
    cursor = None
    while True:
        if cursor:
            params["cursor"] = cursor
        try:
            r = requests.get(endpoint, params=params, proxies=proxies, timeout=10)
            r.raise_for_status()
            data = r.json()
            if data.get("retCode") != 0:
                break
            result = data.get("result", {})
            instruments.extend(result.get("list", []))
            cursor = result.get("nextPageCursor")
            if not cursor:
                break
        except requests.RequestException as e:
            print("Bybit fetch error:", e)
            break
    return instruments

def fetch(endpoint: str,proxies) -> list[dict]:
    try:
        r = requests.get(endpoint, proxies=proxies, timeout=10)
        r.raise_for_status()
        return r.json().get("symbols", [])
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求 {endpoint} 出错:", e)
        return []
def  get_all_token(platform,port):
    # ========= 代理设置 =========
    proxy_host = os.getenv("PROXY_HOST", "127.0.0.1")
    proxy_port = os.getenv("PROXY_PORT", str(port))
    proxy_scheme = os.getenv("PROXY_SCHEME", "http")

    proxies = {
        "http": f"{proxy_scheme}://{proxy_host}:{proxy_port}",
        "https": f"{proxy_scheme}://{proxy_host}:{proxy_port}"
    }

    if platform == "binance":
        fapi_url = "https://fapi.binance.com/fapi/v1/exchangeInfo"  # USDT 本位
        symbols =  fetch(fapi_url,proxies)
       # print(f"已获取 {len(symbols)} 条合约信息\n")
        tokens = []
        rows = []
        for s in symbols:
            pair = s['pair']
            if pair.endswith("USDT"):
                tokens.append(pair[:-4])
       # print(alltoken)
        #return tokens

    elif platform == "bybit":
        instruments = _fetch_bybit(proxies)
        tokens = [i["symbol"][:-4] for i in instruments if i.get("symbol", "").endswith("USDT")]
       # return tokens
    elif platform == "bitget":
        items = _fetch_bitget(proxies, )
        tokens = [item["symbol"][:-4] for item in items if item.get("symbol", "").endswith("USDT")]
      #  return tokens


    if tokens:
        alltokens = []
        for token in tokens:
            alltokens.append(token+"_USDT")
        return alltokens


if __name__ == "__main__":
    biancetoken = get_all_token('bitget',7890)
    print(biancetoken)
    print(1)
