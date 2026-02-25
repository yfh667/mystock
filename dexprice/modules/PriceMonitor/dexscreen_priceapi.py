import requests
import time
from typing import Tuple, List, Set

import json
import urllib3
from numpy.ma.core import minimum

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from datetime import datetime
from dexprice.modules.utilis.define import Config,TokenInfo

# 定义结构体来存储提取的信息
from typing import List
import sys
import dexprice.modules.proxy.testnetwork as testnetwork


def Get_Price_Dexscreen(source_type: int, chain_id: str, pair_addresses: List[str], proxy_port: int = None, ) -> Tuple[
    str, List[str], List[str], str]:
    # base_url = ""
    url = ""
    # 根据 source_type 设置 base_url
    if source_type == Config.DEXS:
        base_url = "https://api.dexscreener.com/latest/dex/pairs/"
        #  url = base_url + chain_id + "/" + pair_addresses[0]
        url = base_url + str(chain_id) + "/" + str(pair_addresses[0])
        for i in range(1, len(pair_addresses)):
            url += "," + pair_addresses[i]
    elif source_type == Config.GECK:
        base_url = "https://api.geckoterminal.com/api/v2/networks/" + chain_id + "/tokens/multi/"
        url = base_url + pair_addresses[0]

        for i in range(1, len(pair_addresses)):
            url += "," + pair_addresses[i]
    elif source_type == Config.DEXCA:

        url = f'https://api.dexscreener.com/latest/dex/tokens/{pair_addresses[0]}'

    max_retries = 5
    retry_count = 0
    proxies = None

    if proxy_port:
        proxy_url = f"http://127.0.0.1:{proxy_port}"
        proxies = {
            'http': proxy_url,
            'https': proxy_url,
        }
    # here we need carefully solve the retries

    while retry_count < max_retries:
        try:
            # 设置 10 秒超时（你可以根据需要调整为 5 或 15）
            response = requests.get(url, proxies=proxies, verify=False, timeout=10)
            #response = requests.get(url, proxies=proxies, verify=False)
            if response.status_code == 200:
                break
            elif response.status_code == 429:
                print("HTTP 429: Too Many Requests. Retrying after a delay.")
                # 这里不需要 return，也不需要 sleep，直接走下面的指数回退
            #    time.sleep(5)  # 等待更长时间
            elif response.status_code == 404:
                print(f"HTTP 404: Not Found. pairaddress: {pair_addresses}")
                # 明确返回 NOT_FOUND，外层可以判断这不是网络问题，而是币不存在
                return "NOT_FOUND"
            elif response.status_code == 400:
                print(f"HTTP 400: Bad Request. Invalid input! pairaddress: {pair_addresses}")
                # 400 也是不可重试的致命错误，直接返回
                return "BAD_REQUEST"
            # elif response.status_code == 404:
            #     # 如果返回404，直接返回错误
            #     print(f"HTTP 404: Not Found. Returning ERROR.")
            #     # here it implies that it is none
            #     return "ERROR"
            else:
                print(f"HTTP error: {response.status_code} pairaddress :{pair_addresses}")
            # print(pair_addresses)
        except requests.RequestException as e:
            print(f"Request failed: {e} pairaddress :{pair_addresses}")
            # here we need check the network is ok or not,if network is down ,we need finish the retry
            if (not testnetwork.test_google_through_proxy(proxy_port)):
                print("Network is down. Exiting retry loop.")
                return "FAILED"  # 网络断开，必须触发外层换代理

        retry_count += 1
        if retry_count < max_retries:
            print(f"Retrying... ({retry_count}/{max_retries})")
            time.sleep(2 ** retry_count)  # 指数回退

    if retry_count == max_retries:
        print("Max retries reached. Exiting.")
        return "FAILED"  # 使用 "ERROR" 字符串表示请求失败

    jsonData = response.json()
    return jsonData



#
# def Get_Price_Dexscreen(source_type: int, chain_id: str, pair_addresses: List[str], proxy_port: int = None,) -> Tuple[str, List[str], List[str], str]:
#     # base_url = ""
#     url = ""
#     # 根据 source_type 设置 base_url
#     if source_type == Config.DEXS:
#         base_url = "https://api.dexscreener.com/latest/dex/pairs/"
#       #  url = base_url + chain_id + "/" + pair_addresses[0]
#         url = base_url + str(chain_id) + "/" + str(pair_addresses[0])
#         for i in range(1, len(pair_addresses)):
#             url += "," + pair_addresses[i]
#     elif source_type == Config.GECK:
#         base_url = "https://api.geckoterminal.com/api/v2/networks/" + chain_id + "/tokens/multi/"
#         url = base_url +pair_addresses[0]
#
#         for i in range(1, len(pair_addresses)):
#             url += "," + pair_addresses[i]
#     elif source_type ==Config.DEXCA:
#
#         url = f'https://api.dexscreener.com/latest/dex/tokens/{pair_addresses[0]}'
#
#     max_retries = 5
#     retry_count = 0
#     proxies = None
#
#     if proxy_port:
#         proxy_url = f"http://127.0.0.1:{proxy_port}"
#         proxies = {
#             'http': proxy_url,
#             'https': proxy_url,
#         }
# # here we need carefully solve the retries
#
#     while retry_count < max_retries:
#         try:
#             response = requests.get(url, proxies=proxies, verify=False)
#             if response.status_code == 200:
#                 break
#             elif response.status_code == 429:
#                 print("HTTP 429: Too Many Requests. Retrying after a delay.")
#                 time.sleep(5)  # 等待更长时间
#
#             elif response.status_code == 404:
#                 # 如果返回404，直接返回错误
#                 print(f"HTTP 404: Not Found. Returning ERROR.")
#                 # here it implies that it is none
#                 return "ERROR"
#             else:
#                 print(f"HTTP error: {response.status_code} pairaddress :{pair_addresses}")
#                # print(pair_addresses)
#         except requests.RequestException as e:
#             print(f"Request failed: {e} pairaddress :{pair_addresses}")
#             # here we need check the network is ok or not,if network is down ,we need finish the retry
#             if(not testnetwork.test_google_through_proxy(proxy_port)):
#                 return "ERROR"
#
#         retry_count += 1
#         if retry_count < max_retries:
#             print(f"Retrying... ({retry_count}/{max_retries})")
#             time.sleep(2 ** retry_count)  # 指数回退
#
#     if retry_count == max_retries:
#         print("Max retries reached. Exiting.")
#         return "ERROR"  # 使用 "ERROR" 字符串表示请求失败
#
#
#     jsonData = response.json()
#     return jsonData


def process_response(source_type, response_json):
    if source_type == Config.DEXS:
        # For DEXS, process reordered response with timestamp
        return process_reordered_response(source_type,response_json, gettime())

    elif source_type == Config.DEXCA:
        # For DEXCA, process to get the pair address with maximum liquidity
        if 'pairs' in response_json:
            pairs = response_json['pairs']
            pairAddress = ''
            chainid = ''

            if pairs:
                chainid = pairs[0]['chainId']
                pairAddress = pairs[0]['pairAddress']

            # max_liquid = 0
            # minimumtime =''
            # if pairs:
            #     for pair in pairs:
            #         liquidity_info = pair.get('liquidity', {})
            #         liquid = liquidity_info.get('usd')
            #     #    createtime = pair.get('pairCreatedAt')
            #         if (not len(chainid) ):
            #             if(pair['chainId']):
            #                 chainid = pair['chainId']
            #
            #         if liquid is not None:
            #             if liquid > max_liquid:
            #                 max_liquid = liquid
            #                 pairAddress = pair['pairAddress']
            #         # if createtime is not None:
            #         #     if minimumtime :
            #         #         if createtime < minimumtime:
            #         #             minimumtime = createtime
            #         #             pairAddress = pair['pairAddress']
            #         #     else:
            #         #         minimumtime = createtime
            #         #         pairAddress = pair['pairAddress']
            #
            #         else:
            #             print("Warning: 'liquidity' or 'usd' key is missing in pair data.")

            return chainid,pairAddress, gettime() if pairAddress else None
        else:
            print("No pairs found.")
            return [], gettime()  # Return an empty list instead of None for consistency





def reorder_response_data(response: str, pair_addresses: List[str]) -> str:
    # Implement any reordering logic if needed
    return response

def gettime() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())


# 定义函数来处理 reordered_response
def process_reordered_response(source_type: int,reordered_response: str, timestamp: str) -> List[TokenInfo]:
    tokens_info = []
    if(source_type == Config.DEXS):
            try:
                #data = json.loads(reordered_response)
                data = reordered_response
                pairs = data.get("pairs", [])

                for pair in pairs:
                    pair_address = pair.get("pairAddress", "")
                    chainid = pair.get("chainId", "")
                    base_token = pair.get("baseToken", {})
                    address = base_token.get("address", "")
                    # here we modify
                 #   name = base_token.get("name", "")
                    name = base_token.get("symbol", "")

                    price_usd = float(pair.get("priceUsd", 0))
                    liquidity_usd = float(pair.get("liquidity", {}).get("usd", 0))
                    fdv = float(pair.get("fdv", 0))
                    creation_time_raw = pair.get("pairCreatedAt", 0)
# 我们把这里的对于buy的判断弄到criteria哪里去
                   #here we need filiter the token,because if buy below 10 ,it is nonsense
                    # txns = pair.get("txns", 0)
                    # buy2 = txns.get("h24", 0)
                    # # 将 creation_time_raw 转换为可读格式
                    # buy = buy2.get("buys", 0)

                    txns_buy = pair.get("txns", 0).get("h1", 0).get("buys", 0)
                    txns_sell = pair.get("txns", 0).get("h1", 0).get("sells", 0)
                    volume = pair.get("volume", 0).get("h1", 0)

                    #fdv这么高但是buy少说吗有问题
                    # if(buy<10 and fdv >1000000):
                    #     continue
                    #
                    # #卖盘没有，说明是貔貅
                    # sellall = buy2.get("sells", 0)
                    # if(sellall<10  and fdv >1000000 ):
                    #     continue


                    creattime = datetime.utcfromtimestamp(creation_time_raw / 1000).strftime('%Y-%m-%d %H:%M:%S')

                    token_info = TokenInfo(
                        chainid=chainid,
                        address=address,
                        name=name,
                        price_usd=price_usd,
                        liquidity_usd=liquidity_usd,
                        fdv=fdv,
                        timestamp=timestamp,
                        creattime=creattime,
                        pair_address=pair_address,
                        txn_buy=txns_buy,
                        txn_sell=txns_sell,
                        volume=volume,
                    )
                    tokens_info.append(token_info)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
            except Exception as e:
                print(f"process_reordered_response : error: {e} and response ;{reordered_response}")

            return tokens_info
    if(source_type == Config.GECK):
        try:
            data = json.loads(reordered_response)
            tokens = data.get("data", [])

            for token in tokens:
                attributes = token.get("attributes", {})
                relationships = token.get("relationships", {})
                top_pools = relationships.get("top_pools", {}).get("data", [])

                address = attributes.get("address", "")
                name = attributes.get("name", "")
                price_usd = float(attributes.get("price_usd", 0))
                fdv = float(attributes.get("fdv_usd", 0))
                pair_address = top_pools[0].get("id", "").split("_")[1] if top_pools else ""

                # Since liquidity is not available, we set it to 0
                liquidity_usd = 0
                creattime = ""


                token_info = TokenInfo(
                    address=address,
                    name=name,
                    price_usd=price_usd,
                    liquidity_usd=liquidity_usd,
                    fdv=fdv,
                    timestamp=timestamp,
                    creattime=creattime,
                    pair_address=pair_address
                )
                tokens_info.append(token_info)

        except json.JSONDecodeError as e:
         print(f"Error decoding JSON: {e}")
        except Exception as e:
         print(f"Unexpected error: {e}")

        return tokens_info



def Get_Token_Dexscreen(source_type: int,chain_id: str, pair_addresses: List[str], proxy_port: int = None,) -> Tuple[str, List[str], List[str], str, List[TokenInfo]]:
  #  print(pair_addresses)
    response = Get_Price_Dexscreen(source_type,chain_id, pair_addresses, proxy_port)
   # print(pair_addresses)

# 只有fiald，我们才需要重新处理
    if response == "FAILED":
      # 如果请求失败，则可以处理失败逻辑（例如，重新放入队列）
      print(f"Request failed for addresses {pair_addresses}. Adding to retry queue.")
      # 可以在此处将 pair_addresses 加入重试队列
      # 例如：failed_tasks.put(pair_addresses)
      return "FAILED"  # 或返回一个指示失败的标志
# 如果我们发现，是别的情况
    elif response in ["NOT_FOUND", "BAD_REQUEST"]:
    # 2. 拦截不可重试的业务错误 (404或400)

        print(f"pair_addresses Error  : Invalid or missing addresses. Skipping {pair_addresses}.")
    # 注意：这里绝对没有任何 self.results.extend() 的操作，完美避开字符串被拆解的坑！
        return []



    tokens_info =[]
    if(source_type == Config.DEXCA  ):
        if(response):
            tokens_info = process_response(source_type,response)
            source_type = Config.DEXS
           # print(tokens_info)
            if tokens_info[0] == '':
                return tokens_info
            pairAddress = []
            chain_id = tokens_info[0]
            pairAddress.append(tokens_info[1])

            response = Get_Price_Dexscreen(source_type,chain_id, pairAddress, proxy_port)

            # 2. 【必须添加】拦截第二次请求的错误！
            if response == "FAILED":
                print(f"Second request failed for address {pairAddress}.")
                return "FAILED"
            elif response in ["NOT_FOUND", "BAD_REQUEST"]:
                print(f"Second request Error: Not found. Skipping {pairAddress}.")
                return []  # 同样返回空列表，终结任务

            tokens_info = process_response(source_type,response)
    else:
        tokens_info = process_response(source_type,response)

    return tokens_info

#
# def Get_Token_Dexscreen(source_type: int,chain_id: str, pair_addresses: List[str], proxy_port: int = None,) -> Tuple[str, List[str], List[str], str, List[TokenInfo]]:
#   #  print(pair_addresses)
#     response = Get_Price_Dexscreen(source_type,chain_id, pair_addresses, proxy_port)
#    # print(pair_addresses)
#
#     if response == "ERROR":
#       # 如果请求失败，则可以处理失败逻辑（例如，重新放入队列）
#       print(f"Request failed for addresses {pair_addresses}. Adding to retry queue.")
#       # 可以在此处将 pair_addresses 加入重试队列
#       # 例如：failed_tasks.put(pair_addresses)
#       return "FAILED"  # 或返回一个指示失败的标志
#
#     tokens_info =[]
#     if(source_type == Config.DEXCA  ):
#         if(response):
#             tokens_info = process_response(source_type,response)
#             source_type = Config.DEXS
#            # print(tokens_info)
#             if tokens_info[0] == '':
#                 return tokens_info
#             pairAddress = []
#             chain_id = tokens_info[0]
#             pairAddress.append(tokens_info[1])
#
#             response = Get_Price_Dexscreen(source_type,chain_id, pairAddress, proxy_port)
#             tokens_info = process_response(source_type,response)
#     else:
#         tokens_info = process_response(source_type,response)
#
#     return tokens_info


def get_liquidmax_pair_addresses(pairs):
    pair_addresses = []
    for pair in pairs:
        if 'labels' not in pair:
            if 'pairAddress' in pairs:
                   pair_addresses.append(pair['pairAddress'])
    return pair_addresses


def get_token_pairs(token_addresses):
    url = f'https://api.dexscreener.com/latest/dex/tokens/{token_addresses}'

    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()  # 解析 JSON 响应
        #  print(data)

        # 处理返回的数据
        if 'pairs' in data:
            return data['pairs']
        else:
            print("No pairs found.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None