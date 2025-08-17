from dexprice.modules.OHLCV.get_token_create_time import get_pool_createtime_with_150d_cap

if __name__ == "__main__":
    network = "bsc"
    pair_address = "0x5181C65117D6421BEF9245b6d064be212eA72589"
    proxy_port = 7890

    info = get_pool_createtime_with_150d_cap(network, pair_address, proxy_port=proxy_port)
    print(info)


    # 可能输出：
    # {'ts': 1723248000, 'time_utc': '2024-08-10 00:00:00', 'is_lower_bound': True}
    # 表示：已触及 150 天上限 -> “创建时间 >= 150 天前”，此时用 150 天的截点当作下界
