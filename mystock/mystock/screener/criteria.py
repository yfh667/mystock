"""定义静态筛选条件，字段对应 Stock 快照指标。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class StaticCriteria:
    """静态指标筛选条件；None 表示该方向不启用。"""

    total_mv_min: Optional[float] = None
    total_mv_max: Optional[float] = None
    circ_mv_min: Optional[float] = None
    circ_mv_max: Optional[float] = None
    turnover_rate_min: Optional[float] = None
    turnover_rate_max: Optional[float] = None
    pe_ratio_min: Optional[float] = None
    pe_ratio_max: Optional[float] = None
    pb_ratio_min: Optional[float] = None
    pb_ratio_max: Optional[float] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    amount_min: Optional[float] = None
    name_exclude: list[str] = field(default_factory=list)

