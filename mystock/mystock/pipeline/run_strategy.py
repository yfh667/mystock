"""读取标的、拉取 K 线、持久化并运行策略。"""
from __future__ import annotations

from ..config import disable_system_proxy
from ..datasource import kline_em, yahoo
from ..datasource.proxy_pool import ProxyPool
from ..db.sqlite_db import StockDB
from ..screener.criteria import StaticCriteria
from ..screener.static_screener import screen as screen_stocks
from ..strategy.base import Strategy, StrategyResult
from ..strategy.runner import run_strategy

# 可选 OHLCV 数据源：模块 + 对应的代理池探活目标。
# yahoo 走 clash 翻墙节点(绕东财限流)，eastmoney 走国内直连。
_SOURCES = {
    "yahoo": (yahoo, "google"),
    "eastmoney": (kline_em, "eastmoney"),
}


def run_market_strategy(
    db_path: str,
    market: str,
    strategy: Strategy,
    *,
    criteria: StaticCriteria | None = None,
    start_date: str,
    end_date: str,
    source: str = "yahoo",
    use_proxy: bool = False,
    max_workers: int = 8,
    persist_ohlcv: bool = True,
    verbose: bool = True,
) -> list[StrategyResult]:
    """对指定市场运行策略，必要时先用静态条件缩小范围。

    :param source: 'yahoo'(走 clash，绕东财限流，推荐) 或 'eastmoney'(国内直连)。
                   yahoo 出口在国外，必须走代理池，故会自动启用。
    """
    if source not in _SOURCES:
        raise ValueError(f"未知数据源 {source}，可选 {list(_SOURCES)}")
    kline_mod, probe_target = _SOURCES[source]

    with StockDB(db_path) as db:
        stocks = db.read_stocks(market)
        if criteria is not None:
            stocks = screen_stocks(stocks, criteria)
        if verbose:
            print(f"[strategy] {market} 待运行 {len(stocks)} 只，数据源={source}")

        disable_system_proxy()
        # yahoo 必须翻墙，强制走代理池；eastmoney 仅在显式 use_proxy 时走。
        proxy_pool = None
        if use_proxy or source == "yahoo":
            proxy_pool = ProxyPool()
            proxy_pool.probe(target=probe_target, verbose=verbose)

        ohlcv_map = kline_mod.fetch_ohlcv_batch(
            stocks,
            start_date=start_date,
            end_date=end_date,
            proxy_pool=proxy_pool,
            max_workers=max_workers,
            verbose=verbose,
        )

        if persist_ohlcv:
            bars = [bar for group in ohlcv_map.values() for bar in group]
            db.upsert_ohlcv(bars)
            if verbose:
                print(f"[strategy] K线入库 {len(bars)} 根")

    results = run_strategy(stocks, ohlcv_map, strategy)
    if verbose:
        print(f"[strategy] 命中 {len(results)} 只")
    return results

