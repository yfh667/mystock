

import dexprice.modules.proxy.clash_api as clash
import dexprice.modules.proxy.getproxy as getproxy
if __name__ == "__main__":
    # 设置要检查的端口范围
    clash_api_url = "http://127.0.0.1:9097"
    headers = {"Authorization": "Bearer manba"}
    proxies = clash.get_all_proxies(clash_api_url,headers)
    #
    # proxynumber = clash.get_proxy_number(proxies)
    # available_ports = getproxy.check_open_ports(50000, proxynumber)
    #
    # print("可用端口:", available_ports)
    proxys =clash.get_one_ip_proxy(50000,clash_api_url,headers)
    print(proxys)

