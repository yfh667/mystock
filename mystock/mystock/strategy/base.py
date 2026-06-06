"""定义策略抽象接口和统一结果结构。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from ..models import Stock, StockOHLCV


@dataclass
class StrategyResult:
    """策略输出；metrics 存放排序和展示用的数值。"""

    stock_id: str
    symbol: str
    market: str
    signal: bool
    reason: str
    metrics: dict = field(default_factory=dict)


class Strategy(ABC):
    """策略基类；调用方保证 bars 按时间升序，策略只读不改。"""

    @abstractmethod
    def evaluate(
        self,
        stock: Stock,
        bars: list[StockOHLCV],
    ) -> Optional[StrategyResult]:
        """评估单只股票，数据不足可返回 None。"""

