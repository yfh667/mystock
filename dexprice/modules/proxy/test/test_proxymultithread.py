import dexprice.modules.proxy.proxymultitheread as proxymultitheread
# 示例调用
if __name__ == "__main__":
    clash_api_url = "http://127.0.0.1:9097"
    headers = {"Authorization": "Bearer manba"}

    startport = 50000
    proxys = proxymultitheread.get_one_ip_proxy_multithread(startport, clash_api_url, headers)

    # 输出获取的可用代理
    for proxy in proxys:
        print(proxy)
    print(len(proxys))