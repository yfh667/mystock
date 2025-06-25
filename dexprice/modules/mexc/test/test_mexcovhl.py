import dexprice.modules.utilis.define as define
import dexprice.modules.mexc.mexcovhl as mexcovhl

import dexprice.modules.utilis.timedefine   as timedefine
#kline_data = mexcovhl.get_kline_data('BTC_USDT', 'Day1', 1740020707, 1740196980,7890)


# get_kline_data('QUAI_USDT', 'Day1', 1739957923, 1739977923, 7890)
#historydatas = mexcovhl.mexc_token_history('BTC_USDT', '1D', 1740036087, 1740196980,7890,0)
# 获取合约K线（默认）
#data = mexcovhl.get_kline_data("BTC_USDT", interval="1D", start=1710000000, end=1710086400)



realdata =mexcovhl.mexc_token_history('BTC_USDT', '1D', 1740036087, 1740196980,7890,1)
# 获取现货K线（需要设置flag=2）
print(realdata)



# #
# realdata =mexcovhl.mexc_token_history('ODINDOGUSDT', '1D', 1708387200, 1741177621,7890,0)
# # 获取现货K线（需要设置flag=0）
# print(realdata)
