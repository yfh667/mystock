"""批量运行策略并整理命中结果。"""
from __future__ import annotations

from ..models import Stock, StockOHLCV
from .base import Strategy, StrategyResult


def _ratio(result: StrategyResult) -> float:
    """缺少 ratio 的策略结果排在后面。"""
    ratio = result.metrics.get("ratio")
    return ratio if isinstance(ratio, (int, float)) else float("-inf")


def run_strategy(
    stocks: list[Stock],
    ohlcv_map: dict[str, list[StockOHLCV]],
    strategy: Strategy,
) -> list[StrategyResult]:
    """对每只股票运行策略，只收集 signal=True 的结果。"""
    results: list[StrategyResult] = []
    for stock in stocks:
        bars = ohlcv_map.get(stock.stock_id, [])
        result = strategy.evaluate(stock, bars)
        if result is not None and result.signal:
            results.append(result)
    results.sort(key=_ratio, reverse=True)
    return results

