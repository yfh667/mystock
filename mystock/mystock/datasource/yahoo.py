"""Yahoo Finance 日K数据源 —— 走 clash 翻墙节点，绕开东方财富的 IP 限流。

适用场景：东财(国内)按 IP 限流，而 clash 节点出口在国外，正好稳定访问 Yahoo。
Yahoo 同时覆盖 A股(.SS/.SZ)、美股、港股(.HK)，OHLCV 用 v8 chart 接口（无需认证）。

接口签名与 kline_em 保持一致，pipeline 可在两个源之间切换：
    fetch_ohlcv(stock, ...)        -> list[StockOHLCV]
    fetch_ohlcv_batch(stocks, ...) -> dict[stock_id, list[StockOHLCV]]
"""
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence

import requests

from ..config import Market
from ..models import Stock, StockOHLCV
from .proxy_pool import ProxyPool

_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
_UA = {"User-Agent": "Mozilla/5.0"}


def to_yahoo_symbol(stock: Stock) -> str:
    """把内部代码转成 Yahoo 代码。

    美股：直接用 symbol(AAPL)。
    A股：6/9 开头沪市加 .SS，0/3 开头深市加 .SZ。
    港股：.HK（若 market 标成 HK）。
    """
    sym = stock.symbol
    if stock.market == Market.US:
        return sym
    if stock.market == Market.A_SHARE:
        suffix = ".SS" if sym[:1] in ("6", "9") else ".SZ"
        return f"{sym}{suffix}"
    return sym  # 其它市场原样返回


def _to_epoch(date_str: str) -> int:
    """'YYYYMMDD' -> unix 时间戳(UTC 当日 0 点)。"""
    dt = datetime.strptime(date_str[:8], "%Y%m%d").replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def _parse_chart(stock: Stock, result: dict, adjust: str = "qfq") -> List[StockOHLCV]:
    """解析 Yahoo chart result，过滤停牌日(null)。

    adjust 非空时按复权因子(adjclose/close)整体复权 OHLC，使历史价连续可比
    （创历史新高判定必须复权，否则除权股会失真）。Yahoo 的 adjclose 是后复权，
    但对"近期最高是否超过历史最高"的判定与前复权结论一致。
    """
    timestamps = result.get("timestamp") or []
    quote = (result.get("indicators", {}).get("quote") or [{}])[0]
    opens, highs = quote.get("open", []), quote.get("high", [])
    lows, closes, vols = quote.get("low", []), quote.get("close", []), quote.get("volume", [])
    adjs = None
    if adjust:
        adjs = (result.get("indicators", {}).get("adjclose") or [{}])[0].get("adjclose")

    out: List[StockOHLCV] = []
    for i, ts in enumerate(timestamps):
        o, h, l, c = opens[i], highs[i], lows[i], closes[i]
        if None in (o, h, l, c):   # 停牌/缺数据
            continue
        factor = 1.0
        if adjs and i < len(adjs) and adjs[i] and c:
            factor = adjs[i] / c   # 复权因子：历史日 <1，最新日 ≈1
        v = vols[i] if i < len(vols) and vols[i] is not None else 0
        day = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
        out.append(StockOHLCV(
            symbol=stock.symbol, market=stock.market, time=day,
            open=float(o) * factor, high=float(h) * factor,
            low=float(l) * factor, close=float(c) * factor,
            volume=float(v), amount=None,   # Yahoo 不提供成交额
        ))
    out.sort(key=lambda x: x.time)
    return out


def fetch_ohlcv(
    stock: Stock,
    *,
    start_date: str = "20200101",
    end_date: str = "20300101",
    adjust: str = "qfq",          # 占位：Yahoo chart 默认未复权，保持签名一致
    timeout: float = 12.0,
    retry: int = 4,
    proxy_pool: Optional[ProxyPool] = None,
    session: Optional[requests.Session] = None,
) -> List[StockOHLCV]:
    """拉取单只股票日K（走代理池）。proxy_pool 存在时每次重试轮换出口。"""
    if session is None:
        session = requests.Session()
        session.trust_env = False
    url = _CHART_URL.format(symbol=to_yahoo_symbol(stock))
    params = {
        "period1": _to_epoch(start_date),
        "period2": _to_epoch(end_date),
        "interval": "1d",
        "events": "div,split",
    }
    last_err: Optional[Exception] = None
    for attempt in range(retry):
        proxies = proxy_pool.get() if proxy_pool else None
        try:
            r = session.get(url, params=params, headers=_UA, timeout=timeout, proxies=proxies)
            r.raise_for_status()
            chart = r.json().get("chart", {})
            results = chart.get("result")
            if not results:
                return []
            return _parse_chart(stock, results[0], adjust=adjust)
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(0.4 * (attempt + 1))
    raise RuntimeError(f"{stock.stock_id} Yahoo日K拉取失败: {last_err!r}")


def fetch_ohlcv_batch(
    stocks: Sequence[Stock],
    *,
    start_date: str = "20200101",
    end_date: str = "20300101",
    adjust: str = "qfq",
    proxy_pool: Optional[ProxyPool] = None,
    max_workers: int = 8,
    verbose: bool = False,
) -> Dict[str, List[StockOHLCV]]:
    """并发批量拉取多只股票日K，返回 {stock_id: [StockOHLCV,...]}。"""
    results: Dict[str, List[StockOHLCV]] = {}
    failed: List[str] = []

    def _one(stk: Stock):
        return stk.stock_id, fetch_ohlcv(
            stk, start_date=start_date, end_date=end_date,
            adjust=adjust, proxy_pool=proxy_pool,
        )

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(_one, s): s for s in stocks}
        done = 0
        for fut in as_completed(futs):
            done += 1
            try:
                sid, bars = fut.result()
                results[sid] = bars
            except Exception:  # noqa: BLE001
                failed.append(futs[fut].stock_id)
            if verbose and done % 50 == 0:
                print(f"[yahoo] {done}/{len(stocks)} 完成，失败 {len(failed)}")

    if verbose:
        print(f"[yahoo] 批量完成 {len(results)}/{len(stocks)}，失败 {len(failed)}")
    return results
