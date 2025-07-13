import dexprice.modules.proxy.clash_api as clash_api
import dexprice.modules.proxy.testproxy as testproxy
import requests
import concurrent.futures
import dexprice.modules.proxy.proxydefine as proxydefine
import dexprice.modules.cex.future.testforcex as testforcex

# 主函数，获取可用 IP 代理
def get_one_ip_proxy_multithread_distinct(startport, clash_api_url, headers,cex_name):
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
            flag = testforcex.cex_test_proxy_port(port=port, platform=cex_name)

            if flag!=-1:

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