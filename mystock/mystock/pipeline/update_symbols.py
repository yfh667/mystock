"""更新股票标的快照并写入数据库。"""
from __future__ import annotations

from ..config import disable_system_proxy
from ..datasource.eastmoney import fetch_snapshot
from ..datasource.proxy_pool import ProxyPool
from ..db.sqlite_db import StockDB


def update_symbols(
    db_path: str,
    markets: list[str],
    use_proxy: bool = False,
    verbose: bool = True,
) -> dict[str, int]:
    """按市场拉取快照，返回每个市场的入库数量。"""
    disable_system_proxy()
    proxy_pool = None
    if use_proxy:
        proxy_pool = ProxyPool()
        proxy_pool.probe(verbose=verbose)

    counts: dict[str, int] = {}
    with StockDB(db_path) as db:
        for market in markets:
            stocks = fetch_snapshot(market, proxy_pool=proxy_pool, verbose=verbose)
            counts[market] = db.upsert_stocks(stocks)
            if verbose:
                print(f"[update-symbols] {market} 入库 {counts[market]} 只")
    return counts

