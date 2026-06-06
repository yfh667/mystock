"""东方财富数据源：分页拉取全市场快照。

对标原项目里"从交易所拿全部 token 列表 + 指标"那一层。
一次性大请求(pz=50000)会被服务端掐断，所以按 EM_PAGE_SIZE 分页，
并在多个 host 间轮询容灾。
"""
from __future__ import annotations

import time
from typing import List, Optional

import requests

from ..config import (
    EM_CLIST_HOSTS,
    EM_FIELD_MAP,
    EM_FIELDS,
    EM_MARKET_FS,
    EM_PAGE_SIZE,
    Market,
)
from ..models import Stock
from .proxy_pool import ProxyPool


def _new_session() -> requests.Session:
    """绕过系统代理直连东方财富。"""
    s = requests.Session()
    s.trust_env = False
    s.headers.update({"User-Agent": "Mozilla/5.0 (mystock)"})
    return s


def _get_with_failover(
    session: requests.Session, params: dict, timeout: float, proxies: Optional[dict] = None
) -> dict:
    """在多个东财 host 间轮询请求，任一成功即返回 json['data']。

    :param proxies: 指定出口(来自代理池)；None 表示按 session 设置(直连)。
    """
    last_err: Optional[Exception] = None
    for host in EM_CLIST_HOSTS:
        try:
            r = session.get(host, params=params, timeout=timeout, proxies=proxies)
            r.raise_for_status()
            return r.json().get("data") or {}
        except Exception as e:  # noqa: BLE001 —— 容灾，继续试下一个 host
            last_err = e
            continue
    raise RuntimeError(f"东方财富所有 host 均请求失败: {last_err!r}")


def _row_to_stock(row: dict, market: str) -> Optional[Stock]:
    """把东财一行原始字段转成 Stock；缺代码则丢弃。"""
    symbol = row.get("f12")
    if not symbol:
        return None

    kwargs = {}
    for em_key, field_name in EM_FIELD_MAP.items():
        if field_name in ("symbol", "name"):
            continue
        val = row.get(em_key)
        # 东财用 '-' 表示无数据
        kwargs[field_name] = None if val in (None, "-", "") else val

    # 东财内部代码 secid = '市场id.代码'（f13 是市场id：沪1/深0/纳105/纽106/美交所107）。
    # 统一成 secid 格式，K线接口(kline_em)直接拿它用；A股纯代码仍在 symbol 字段。
    em_market_id = row.get("f13")
    raw_code = f"{em_market_id}.{symbol}" if em_market_id is not None else symbol

    return Stock(
        symbol=symbol,
        name=row.get("f14") or "",
        market=market,
        raw_code=raw_code,
        **kwargs,
    )


def fetch_snapshot(
    market: str,
    *,
    timeout: float = 15.0,
    retry_per_page: int = 4,
    proxy_pool: Optional[ProxyPool] = None,
    verbose: bool = False,
) -> List[Stock]:
    """拉取某市场全部股票的实时快照（标的 + 静态指标）。

    :param market: Market.A_SHARE 或 Market.US
    :param proxy_pool: 可选代理池；提供时每页/每次重试轮换出口 IP，绕开单 IP 限流。
                       不提供则本机直连（需先 disable_system_proxy()）。
    :return: Stock 列表（含总市值/换手率/市盈率等筛选指标）
    """
    fs = EM_MARKET_FS[market]
    session = _new_session()
    # f13 用于拼美股内部代码，附加到业务字段之外
    fields = EM_FIELDS + ",f13"

    stocks: List[Stock] = []
    seen = set()
    pn = 1
    total = None
    t0 = time.time()

    while True:
        params = {
            "pn": pn,
            "pz": EM_PAGE_SIZE,
            "po": 1,
            "np": 1,
            "fltt": 2,
            "invt": 2,
            "fid": "f3",
            "fs": fs,
            "fields": fields,
        }

        data = None
        for attempt in range(retry_per_page):
            proxies = proxy_pool.get() if proxy_pool else None
            try:
                data = _get_with_failover(session, params, timeout, proxies)
                break
            except Exception:  # noqa: BLE001
                if attempt == retry_per_page - 1:
                    raise
                time.sleep(0.5 * (attempt + 1))

        diff = (data or {}).get("diff")
        if total is None:
            total = (data or {}).get("total", 0)
        if not diff:
            break

        # diff 可能是 list 或 dict（东财两种返回形态都见过）
        rows = diff.values() if isinstance(diff, dict) else diff
        page_count = 0
        for row in rows:
            page_count += 1
            stock = _row_to_stock(row, market)
            if stock is None or stock.symbol in seen:
                continue
            seen.add(stock.symbol)
            stocks.append(stock)

        if verbose:
            print(f"[eastmoney:{market}] page {pn} +{page_count} 累计 {len(stocks)}/{total}")

        if page_count == 0 or (total and len(seen) >= total):
            break
        pn += 1

    if verbose:
        print(f"[eastmoney:{market}] 完成 {len(stocks)} 只，用时 {time.time() - t0:.1f}s")
    return stocks
