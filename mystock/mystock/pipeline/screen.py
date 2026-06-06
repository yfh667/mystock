"""从数据库读取股票并执行静态筛选。"""
from __future__ import annotations

from ..db.sqlite_db import StockDB
from ..models import Stock
from ..screener.criteria import StaticCriteria
from ..screener.static_screener import screen as screen_stocks


def screen_market(
    db_path: str,
    market: str,
    criteria: StaticCriteria,
    verbose: bool = True,
) -> list[Stock]:
    """筛选指定市场的已入库标的。"""
    with StockDB(db_path) as db:
        stocks = db.read_stocks(market)
    matched = screen_stocks(stocks, criteria)
    if verbose:
        print(f"[screen] {market} 命中 {len(matched)}/{len(stocks)} 只")
    return matched

