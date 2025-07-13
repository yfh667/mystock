def get_kline_data(symbol, interval="Min15", start=None, end=None,port=7890):
    url = f"https://contract.mexc.com/api/v1/contract/kline/index_price/{symbol}"
    params = {"interval": interval}

    if start:
        params["start"] = start
    if end:
        params["end"] = end
    httpurl = "http://127.0.0.1:"+str(port)

    proxies = {
        "http": httpurl,
        "https": httpurl
    }

    # 生成完整 URL 并打印
    full_url = requests.Request('GET', url, params=params).prepare().url
  #  print(f"Request URL: {full_url}")

    response = requests.get(url, params=params,proxies=proxies)

    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            return data["data"]
        else:
            print("API Response Error:", data)
            print(f"the token is {symbol}")
    else:
        print("HTTP Request Failed with Status Code:", response.status_code)

    return None
