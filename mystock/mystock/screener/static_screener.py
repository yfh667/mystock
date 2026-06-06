"""执行静态快照筛选，只使用 Stock 已入库字段。"""
from __future__ import annotations

from ..models import Stock
from .criteria import StaticCriteria


def _below_min(value: float | None, limit: float | None) -> bool:
    """数据源缺值时跳过比较，避免把未知误判为不合格。"""
    return value is not None and limit is not None and value < limit


def _above_max(value: float | None, limit: float | None) -> bool:
    """数据源缺值时跳过比较，避免把未知误判为不合格。"""
    return value is not None and limit is not None and value > limit


def match(stock: Stock, c: StaticCriteria) -> bool:
    """判断单只股票是否满足静态筛选条件。"""
    name = stock.name or ""
    name_upper = name.upper()
    for word in c.name_exclude:
        if word and word.upper() in name_upper:
            return False

    if _below_min(stock.total_mv, c.total_mv_min):
        return False
    if _above_max(stock.total_mv, c.total_mv_max):
        return False
    if _below_min(stock.circ_mv, c.circ_mv_min):
        return False
    if _above_max(stock.circ_mv, c.circ_mv_max):
        return False
    if _below_min(stock.turnover_rate, c.turnover_rate_min):
        return False
    if _above_max(stock.turnover_rate, c.turnover_rate_max):
        return False
    if _below_min(stock.pe_ratio, c.pe_ratio_min):
        return False
    if _above_max(stock.pe_ratio, c.pe_ratio_max):
        return False
    if _below_min(stock.pb_ratio, c.pb_ratio_min):
        return False
    if _above_max(stock.pb_ratio, c.pb_ratio_max):
        return False
    if _below_min(stock.price, c.price_min):
        return False
    if _above_max(stock.price, c.price_max):
        return False
    if _below_min(stock.amount, c.amount_min):
        return False

    return True


def screen(stocks: list[Stock], c: StaticCriteria) -> list[Stock]:
    """过滤股票列表，保留命中条件的标的。"""
    return [stock for stock in stocks if match(stock, c)]

