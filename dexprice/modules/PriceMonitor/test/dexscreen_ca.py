import requests
import dexprice.modules.PriceMonitor.dexscreen_priceapi as dexscreen_priceapi
from dexprice.modules.utilis.define import Config,TokenInfo
#
# def get_token_pairs(token_addresses):
#     url = f'https://api.dexscreener.com/latest/dex/tokens/{token_addresses}'
#
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # 检查请求是否成功
#         data = response.json()  # 解析 JSON 响应
#       #  print(data)
#
#         # 处理返回的数据
#         if 'pairs' in data:
#             return data['pairs']
#         else:
#             print("No pairs found.")
#             return None
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching data: {e}")
#         return None
#
# def get_liquidmax_pair_addresses(pairs):
#
#     if 'pairAddress' in pair:
#      #   pair_addresses.append(pair['pairAddress'])
#         return pair['pairAddress']

if __name__ == '__main__':

    ca_addresses = ["0x19Ed254efa5E061D28d84650891a3db2A9940C16"]

    proxy_port = 7890  # 示例代理端口    chain_id = "solana"  # 这里使用示例的链 ID

    tokens_info = dexscreen_priceapi.Get_Token_Dexscreen(Config.DEXCA,'', ca_addresses, proxy_port)
    pairaddress = []

    print(tokens_info)

