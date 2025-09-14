
from dexprice.modules.utilis.define import FilterCriteria

import dexprice.modules.PriceMonitor.tokenflitter as tokenflitter

import dexprice.modules.proxy.proxymultitheread as proxymultitheread

import dexprice.modules.PriceMonitor.dexscreen_parrel as dexscreen_parrel

import dexprice.modules.utilis.define as define
import dexprice.modules.proxy.proxydefine as proxydefine

#import dexprice.modules.db.insert_db as insert_db
import dexprice.modules.db.insert_db as insert_db

import dexprice.modules.proxy.clash_api as clash
import dexprice.modules.proxy.testproxy as testproxy
import os
import dexprice.modules.utilis.findroot as findroot

def extract_valid_tokens(token_new,criteria):
    # 初始化字典，用链名作为键，地址列表作为值
    chain_addresses = {
        'solana': [],
        'base': [],
        'ethereum': [],
        'bsc': []
    }

    # 遍历 token_new，根据链名将地址加入对应的列表
    for token in token_new:
        # 确保 token.chainid 是链名，并存在于字典的键中
        if token.chainid in chain_addresses:
            chain_addresses[token.chainid].append(token.pair_address)  # 添加地址到对应链的列表
    # all the token that satisfied the request
    tokenreal = []
    # # 示例：打印每个链名及其对应的地址列表

    sourcetype = define.Config.DEXS
    max_threads_per_proxy = 2
    clash_api_url = "http://127.0.0.1:9097"
    headers = {"Authorization": "Bearer manba"}
    rate = 5
    capacity = 300
    startport = 50000
    for chain, pairaddresses in chain_addresses.items():
        print(f"we check Chain: {chain} ")
        chainid = chain

        proxys = proxymultitheread.get_one_ip_proxy_multithread(startport, clash_api_url, headers)
        task_manager = dexscreen_parrel.TaskManager(pairaddresses, sourcetype, chainid, proxys, rate, capacity,
                                                    max_threads_per_proxy, 'get  ' + chainid)
        tokensinfo, failed_tasks = task_manager.run()
        for token in tokensinfo:

            if (tokenflitter.normal_token_filter(token, criteria)):
                if (token.creattime == '1970-01-01 00:00:00'):
                    pass
                else:
                    tokenreal.append(token)

    return tokenreal
