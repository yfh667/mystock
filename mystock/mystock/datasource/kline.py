"""日K(OHLCV)数据源 —— 基于 akshare。

对标原项目从交易所拉 K线那一层。A股与美股走 akshare 不同接口，
统一转成 StockOHLCV 列表返回。
"""
from __future__ import annotations

from typing import List, Optional

from ..config import Market
from ..models import StockOHLCV

# akshare 返回的中文列名 -> 标准字段
_COL_MAP = {
    "日期": "time",
    "开盘": "open",
    "最高": "high",
    "最低": "low",
    "收盘": "close",
    "成交量": "volume",
    "成交额": "amount",
}


def _norm_date(s: str) -> str:
    """统一成 'YYYY-MM-DD' 字符串。"""
    return str(s)[:10]


def fetch_ohlcv(
    symbol: str,
    market: str,
    *,
    start_date: str = "20200101",
    end_date: str = "20300101",
    adjust: str = "qfq",
    raw_code: Optional[str] = None,
) -> List[StockOHLCV]:
    """拉取单只股票的日K线。

    :param symbol: 干净代码（A股 600519 / 美股 AAPL）
    :param market: Market.A_SHARE / Market.US
    :param start_date/end_date: 'YYYYMMDD'
    :param adjust: 'qfq' 前复权 / 'hfq' 后复权 / '' 不复权
    :param raw_code: 东财内部代码；美股必须传(如 '105.AAPL')，A股可省略
    :return: 按时间升序的 StockOHLCV 列表
    """
    import akshare as ak  # 延迟导入，避免无谓的启动开销

    if market == Market.A_SHARE:
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
        )
    elif market == Market.US:
        code = raw_code or symbol
        df = ak.stock_us_hist(
            symbol=code,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
        )
    else:
        raise ValueError(f"未知市场: {market}")

    if df is None or df.empty:
        return []

    out: List[StockOHLCV] = []
    for _, row in df.iterrows():
        rec = {std: row[cn] for cn, std in _COL_MAP.items() if cn in df.columns}
        out.append(
            StockOHLCV(
                symbol=symbol,
                market=market,
                time=_norm_date(rec["time"]),
                open=float(rec["open"]),
                high=float(rec["high"]),
                low=float(rec["low"]),
                close=float(rec["close"]),
                volume=float(rec.get("volume", 0) or 0),
                amount=(float(rec["amount"]) if rec.get("amount") not in (None, "") else None),
            )
        )
    out.sort(key=lambda x: x.time)
    return out
