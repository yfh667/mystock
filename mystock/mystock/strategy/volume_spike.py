"""成交量或成交额放量策略。"""
from __future__ import annotations

from typing import Optional

from ..models import Stock, StockOHLCV
from .base import Strategy, StrategyResult


class VolumeSpikeStrategy(Strategy):
    """当日量显著高于过去 N 日均量时给出信号。"""

    def __init__(self, lookback: int = 10, multiple: float = 10.0, use: str = "volume"):
        if lookback <= 0:
            raise ValueError("lookback 必须大于 0")
        if multiple <= 0:
            raise ValueError("multiple 必须大于 0")
        if use not in ("volume", "amount"):
            raise ValueError("use 只能是 'volume' 或 'amount'")
        self.lookback = lookback
        self.multiple = multiple
        self.use = use

    def _value(self, bar: StockOHLCV) -> Optional[float]:
        """amount 可能缺失，缺失时不强行计算。"""
        if self.use == "amount":
            return bar.amount
        return bar.volume

    def evaluate(
        self,
        stock: Stock,
        bars: list[StockOHLCV],
    ) -> Optional[StrategyResult]:
        """评估最后一根 K 线是否发生放量。"""
        if len(bars) < self.lookback + 1:
            return None

        today = self._value(bars[-1])
        history = [self._value(bar) for bar in bars[-self.lookback - 1:-1]]
        if today is None or any(value is None for value in history):
            return None

        avg = sum(history) / self.lookback
        ratio = float("inf") if avg == 0 and today > 0 else (today / avg if avg else 0.0)
        signal = today > avg * self.multiple
        label = "成交额" if self.use == "amount" else "成交量"
        reason = (
            f"当日{label}={today:.2f}，过去{self.lookback}日均值={avg:.2f}，"
            f"放大{ratio:.2f}倍"
        )

        return StrategyResult(
            stock_id=stock.stock_id,
            symbol=stock.symbol,
            market=stock.market,
            signal=signal,
            reason=reason,
            metrics={"today": today, "avg": avg, "ratio": ratio},
        )

