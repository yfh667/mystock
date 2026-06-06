"""数据模型 —— 对标原项目 modules/utilis/define.py。

映射关系：
    crypto TokenInfo/Tokendb   ->  Stock        （标的 + 静态指标快照）
    crypto TokenPriceHistory   ->  StockOHLCV   （K线，字段几乎一致）
    crypto FilterCriteria      ->  见 screener/criteria.py
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Stock:
    """一只股票的基本信息 + 当前静态指标快照。

    既承担原项目 Tokendb（入库标的）的角色，也带上用于筛选的指标字段
    （总市值/换手率/市盈率等），对标 crypto 的 fdv/liquidity。
    """

    symbol: str                       # 股票代码：A股如 600519，美股如 AAPL
    name: str                         # 名称
    market: str                       # 市场：Market.A_SHARE / Market.US

    # 东方财富内部代码：A股为纯代码(600519)，美股带市场前缀(105.AAPL)。
    # 拉日K时需要它（akshare 美股接口要求 '市场id.代码' 格式）。
    raw_code: Optional[str] = None

    # —— 静态指标（来自实时快照，可为空）——
    price: Optional[float] = None             # 最新价
    pct_change: Optional[float] = None        # 涨跌幅 %
    volume: Optional[float] = None            # 成交量
    amount: Optional[float] = None            # 成交额（元）
    turnover_rate: Optional[float] = None     # 换手率 %
    pe_ratio: Optional[float] = None          # 市盈率(动)
    pb_ratio: Optional[float] = None          # 市净率
    total_mv: Optional[float] = None          # 总市值（元）—— 对标 fdv
    circ_mv: Optional[float] = None           # 流通市值（元）—— 对标 liquidity

    list_date: Optional[str] = None           # 上市日期（对标 creattime）

    @property
    def stock_id(self) -> str:
        """全局唯一键：市场 + 代码（美股 AAPL 与某 A股代码不冲突）。"""
        return f"{self.market}:{self.symbol}"


@dataclass
class StockOHLCV:
    """单根 K 线 —— 对标 crypto 的 TokenPriceHistory。

    字段与原项目 price_history 表完全对齐，额外保留成交额 amount。
    """

    symbol: str
    market: str
    time: str                 # 交易日 'YYYY-MM-DD'（或带时分，预留分钟线）
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: Optional[float] = None   # 成交额（元），A股有、美股可空

    @property
    def stock_id(self) -> str:
        return f"{self.market}:{self.symbol}"
