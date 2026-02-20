import dexprice.modules.proxy.clash_api as clash_api
import dexprice.modules.proxy.testproxy as testproxy
import requests
import  dexprice.modules.OHLCV.geck as geck
import concurrent.futures
import dexprice.modules.proxy.proxydefine as proxydefine
import time
import datetime
# 主函数，获取可用 IP 代理

def get_one_ip_proxy_multithread(startport, clash_api_url, headers):
    proxies = clash_api.get_all_proxies(clash_api_url, headers)
    if proxies is None:
        return []

    proxynumber = clash_api.get_proxy_number(proxies)
    ports = [startport + i for i in range(proxynumber)]
    proxys = []
    ips = set()  # 使用集合存储已获取的 IP，防止重复

    # 定义在线程中执行的辅助函数
    def test_proxy(port):
        socksproxy = f'127.0.0.1:{port}'
        ip = testproxy.fetch_public_ip_via_http_proxy(socksproxy)
        if ip is not None:
            return (port, ip)
        return None

    # 使用线程池执行代理测试
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(test_proxy, port): port for port in ports}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result is not None:
                port, ip = result
                if ip not in ips:
                    ips.add(ip)  # 添加到已处理 IP 集合
                    proxy = proxydefine.Proxy(port, ip)
                    proxys.append(proxy)
                else:
                    print(f"Duplicate IP {ip} found on port {port}, skipping.")
    return proxys




def get_one_ip_proxy_multithread_geck(startport, clash_api_url, headers):
    """
    多线程测试从 Clash 暴露的本地连续端口（从 startport 起，数量由 Clash 返回的代理数决定）中，
    哪些端口在当前网络环境下可以“通过代理”成功拉取 GeckoTerminal 的 1d OHLCV 数据。
    满足：
      1) 能通过代理正常建立连接并返回 HTTP 响应；
      2) geck.get_token_history2 返回的 OHLCV 数据非空；
    即认为该端口对应的代理“可用”。

    说明：
    - 函数签名保持不变。
    - 仍使用出口 IP 去重（若无法获取出口 IP，则用代理地址占位去重）。
    """

    proxies = clash_api.get_all_proxies(clash_api_url, headers)
    if proxies is None:
        return []

    # === 业务参数（如需固定，可在此处填写你要测的对象） ===
    network = "bsc"
    # 示例：池地址（如你 geck.get_token_history2 走的是 pool 的 K 线）
    pool_address = ['0x7F0B9A92fe7ABBC64d38cbD02a3c39191657b8bB']
    timeframe = "day"         # 可选: day / hour / minute
    aggregate = "1"           # 聚合粒度
    # “before_timestamp” 用当前时间做上限更稳妥； 因为geck的api只能获取半年内的ovhl数据
    current_time = datetime.datetime.now(datetime.UTC)
    before_timestamp = int(current_time.timestamp())  # 转成整数型时间戳
    # before_timestamp = 1755431848
    # before_timestamp = int(current_time.timestamp())  # 转成整数型时间戳

    limit = 1
    currency = "usd"
    token = "base"            # 若 geck.get_token_history2 需要 token 字段，这里保留原值

    proxynumber = clash_api.get_proxy_number(proxies)
    ports = [startport + i for i in range(proxynumber)]
    proxys = []
    seen_keys = set()  # 用于去重（优先用出口 IP；拿不到时用代理地址）

    def _looks_like_valid_ohlcv(resp_obj) -> bool:
        """
        粗判 geck.get_token_history2 返回是否包含有效的 1d OHLCV。
        你可根据该函数真实返回结构再做定制。
        """
        if resp_obj is None:
            return False
        # 常见：list/tuple 且非空；或 dict 且包含 data/attributes 等关键字段
        if isinstance(resp_obj, (list, tuple)):
            return len(resp_obj) > 0
        if isinstance(resp_obj, dict):
            if "data" in resp_obj and isinstance(resp_obj["data"], list) and resp_obj["data"]:
                return True
            # 有些实现直接把蜡烛数组放在某个键里
            for k in ("candles", "ohlcv", "items"):
                if k in resp_obj and isinstance(resp_obj[k], list) and resp_obj[k]:
                    return True
        return False

    # 在线程中执行的辅助函数：对单个端口进行真实请求测试
    def test_proxy(port):
        socksproxy = f"127.0.0.1:{port}"
        proxy_port = port  # 修正：使用当前端口作为 geck.get_token_history2 的代理端口入参
        try:
            # 若你需要先做一次极轻的连通探测，可在此加一个 HEAD/GET 到 geck 域名；否则直接业务调用：
            ohlcv_data = geck.get_ohlcv_data_with_proxy_lite(
                network=network,
                pool_address=pool_address,
                timeframe=timeframe,
                aggregate=aggregate,
                before_timestamp=before_timestamp,
                limit=limit,
                currency=currency,
                token=token,
                proxy_port=proxy_port,  # 原来未定义，这里修正
            )


            if not  ohlcv_data:
                return None

            # 通过出口 IP 去重；如果拿不到，则退化为用代理地址
            ip = testproxy.fetch_public_ip_via_http_proxy(socksproxy)
            key = ip or socksproxy
            return (port, key)

        except requests.Timeout:
            return None
        except Exception:
            # 建议在调试时打开日志
            # print(f"[DEBUG] port {port} failed: {e}")
            return None

  # max_workers = min(32, max(1, len(ports)))
    max_workers = min(10, max(1, len(ports)))  # 降低并发数
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(test_proxy, port): port for port in ports}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result is None:
                continue
            port, key = result
            if key in seen_keys:
                print(f"Duplicate key {key} found on port {port}, skipping.")
                continue
            seen_keys.add(key)
            proxy = proxydefine.Proxy(port, key)
            proxys.append(proxy)

    return proxys