"""全局配置：市场常量、东方财富接口字段映射、网络直连设置。

要点：东方财富（push2.eastmoney.com）同时提供 A股与美股数据，国内可直连，
不需要走 clash 代理。但本机设置了 Windows 系统级代理(127.0.0.1:7999)，
requests 默认会读取它并导致国内接口被拦，因此这里统一关闭代理。
"""
from __future__ import annotations

import os


def disable_system_proxy() -> None:
    """让本进程内的所有 requests 调用绕过系统代理，直连数据源。

    放在程序入口调用一次即可。等价于给每个 Session 设 trust_env=False，
    但更省事：通过 NO_PROXY=* 让 urllib/requests 对所有主机都不走代理。
    """
    os.environ["NO_PROXY"] = "*"
    os.environ["no_proxy"] = "*"


# ===================== 市场常量 =====================
class Market:
    """标的所属市场（对标原项目里的 chainid）。"""

    A_SHARE = "A"   # 沪深 A 股
    US = "US"       # 美股（纳斯达克 / 纽交所 / 美交所）


# 东方财富 clist 接口的市场过滤参数 fs。
# A股：m:0 t:6/t:80 = 深A，m:1 t:2/t:23 = 沪A（含科创/创业板）。
# 美股：m:105 纳斯达克，m:106 纽交所，m:107 美交所。
EM_MARKET_FS = {
    Market.A_SHARE: "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23",
    Market.US: "m:105,m:106,m:107",
}

# 东方财富 clist 接口分页基址（82/2/... 任一节点均可，做容灾轮询）。
EM_CLIST_HOSTS = [
    "https://82.push2.eastmoney.com/api/qt/clist/get",
    "https://push2.eastmoney.com/api/qt/clist/get",
]

# 单页条数：实测大请求(pz=50000)会被服务端掐断(RemoteDisconnected)，
# 用 100/页分页最稳。
EM_PAGE_SIZE = 100

# ===================== 字段映射 =====================
# 东方财富 clist 字段编号 -> 业务字段名。这些就是"像 fdv 一样筛选"所需的指标。
# 价格类字段当 fltt=2 时已是真实值（无需再除以 100）。
EM_FIELD_MAP = {
    "f12": "symbol",          # 代码
    "f14": "name",            # 名称
    "f2": "price",            # 最新价
    "f3": "pct_change",       # 涨跌幅 %
    "f5": "volume",           # 成交量（手/股）
    "f6": "amount",           # 成交额（元）
    "f8": "turnover_rate",    # 换手率 %
    "f9": "pe_ratio",         # 市盈率(动)
    "f20": "total_mv",        # 总市值（元）—— 对标 crypto 的 fdv
    "f21": "circ_mv",         # 流通市值（元）—— 对标 liquidity
    "f23": "pb_ratio",        # 市净率
}

# 请求时拼给东方财富的 fields 串（即上面 map 的所有 key）。
EM_FIELDS = ",".join(EM_FIELD_MAP.keys())
