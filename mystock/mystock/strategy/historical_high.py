"""创历史新高策略。

选股原则（用户需求）：近一个月的价格走势超过以前任何时候，
即"最近 recent_days 个交易日内的最高价 >= 此前全部历史的最高价"——
历史最高点恰好出现在最近一个月内（刷新或追平历史高点）。

"历史"有多长由传入的 bars 决定：传全部历史 = 真·历史新高；
只传近 30 个月 = 30 个月新高。脚本侧通过拉取范围控制。
"""
from __future__ import annotations

from typing import Optional

from ..models import Stock, StockOHLCV
from .base import Strategy, StrategyResult


class HistoricalHighStrategy(Strategy):
    """近一个月最高价刷新此前历史最高价则给出信号。"""

    def __init__(self, recent_days: int = 22, use: str = "high"):
        """:param recent_days: "近一个月"对应的交易日数（约 22）。
        :param use: 'high' 看最高价（默认，符合"历史最高价"）；'close' 看收盘价（避免盘中插针）。
        """
        if recent_days <= 0:
            raise ValueError("recent_days 必须大于 0")
        if use not in ("high", "close"):
            raise ValueError("use 只能是 'high' 或 'close'")
        self.recent_days = recent_days
        self.use = use

    def _value(self, bar: StockOHLCV) -> float:
        return bar.high if self.use == "high" else bar.close

    def evaluate(self, stock: Stock, bars: list[StockOHLCV]) -> Optional[StrategyResult]:
        # 至少要有"近一个月"+ 之前若干天，否则无从比较历史
        if len(bars) < self.recent_days + 1:
            return None

        recent = bars[-self.recent_days:]
        prior = bars[: -self.recent_days]

        recent_high = max(self._value(b) for b in recent)
        prior_high = max(self._value(b) for b in prior)
        all_time_high = max(recent_high, prior_high)

        # 近一个月最高 >= 此前历史最高 => 历史高点落在最近一个月内
        signal = recent_high >= prior_high

        # 找出近一个月内创出新高的那一天
        peak_day = next(
            (b.time for b in reversed(recent) if self._value(b) == recent_high),
            recent[-1].time,
        )

        label = "最高价" if self.use == "high" else "收盘价"
        if signal:
            reason = (
                f"近{self.recent_days}日{label}={recent_high:.2f} 刷新此前历史最高"
                f"={prior_high:.2f}，于 {peak_day} 创历史新高"
            )
        else:
            reason = (
                f"近{self.recent_days}日{label}={recent_high:.2f} 未超过历史最高"
                f"={prior_high:.2f}"
            )

        return StrategyResult(
            stock_id=stock.stock_id,
            symbol=stock.symbol,
            market=stock.market,
            signal=signal,
            reason=reason,
            metrics={
                "recent_high": recent_high,
                "prior_high": prior_high,
                "all_time_high": all_time_high,
                "peak_day": peak_day,
                # 距历史高点的位置：>=1 表示创新高
                "ratio": (recent_high / prior_high) if prior_high else 0.0,
                "bars": len(bars),
            },
        )
