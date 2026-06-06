"""东方财富原生日K接口 —— 支持代理池轮换 + 并发批量拉取。

相比 akshare 版(kline.py)，这里直接打东财 HTTP 接口，因此能：
    - 走 clash 代理池绕开单 IP 限流
    - 多线程并发批量拉取几千只股票的 OHLCV（跑全市场策略时提速）

secid 用 Stock.raw_code（'1.600519' / '0.000001' / '105.AAPL'）。
"""
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Sequence

import requests

from ..models import Stock, StockOHLCV
from .proxy_pool import ProxyPool

_KLINE_URL = "https://push2his.eastmoney.com/api/qt/stock/kline/get"

# 复权类型：'qfq'前复权 / 'hfq'后复权 / '' 不复权
_FQT = {"qfq": 1, "hfq": 2, "": 0, None: 0}


def _secid_for(stock: Stock) -> str:
    """取 secid。raw_code 已是 secid 格式则直接用；否则按 A股代码规则推断市场。"""
    if stock.raw_code and "." in stock.raw_code:
        return stock.raw_code
    code = stock.symbol
    # 沪市：6/9 开头及 688(科创)；深市：0/3 开头
    market_id = 1 if code[:1] in ("6", "9") else 0
    return f"{market_id}.{code}"


def _parse_klines(stock: Stock, klines: Sequence[str]) -> List[StockOHLCV]:
    """东财 klines 每行: 日期,开,收,高,低,成交量,成交额,振幅,涨跌幅,涨跌额,换手率"""
    out: List[StockOHLCV] = []
    for line in klines:
        p = line.split(",")
        if len(p) < 7:
            continue
        out.append(StockOHLCV(
            symbol=stock.symbol, market=stock.market, time=p[0][:10],
            open=float(p[1]), close=float(p[2]), high=float(p[3]), low=float(p[4]),
            volume=float(p[5]), amount=float(p[6]),
        ))
    out.sort(key=lambda x: x.time)
    return out


def fetch_ohlcv(
    stock: Stock,
    *,
    start_date: str = "20200101",
    end_date: str = "20300101",
    adjust: str = "qfq",
    timeout: float = 12.0,
    retry: int = 4,
    proxy_pool: Optional[ProxyPool] = None,
    session: Optional[requests.Session] = None,
) -> List[StockOHLCV]:
    """拉取单只股票日K。代理池存在时每次重试轮换出口 IP。"""
    if session is None:
        session = requests.Session()
        session.trust_env = False
    params = {
        "secid": _secid_for(stock),
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "klt": 101,  # 日K
        "fqt": _FQT.get(adjust, 1),
        "beg": start_date,
        "end": end_date,
        "lmt": 100000,
    }
    last_err: Optional[Exception] = None
    for attempt in range(retry):
        proxies = proxy_pool.get() if proxy_pool else None
        try:
            r = session.get(_KLINE_URL, params=params, timeout=timeout, proxies=proxies)
            r.raise_for_status()
            data = r.json().get("data")
            if not data or not data.get("klines"):
                return []
            return _parse_klines(stock, data["klines"])
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(0.4 * (attempt + 1))
    raise RuntimeError(f"{stock.stock_id} 日K拉取失败: {last_err!r}")


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
    """并发批量拉取多只股票日K，返回 {stock_id: [StockOHLCV,...]}。

    跑全市场策略时用这个 —— 多线程 + 代理池轮换，既快又抗限流。
    """
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
                print(f"[kline_em] {done}/{len(stocks)} 完成，失败 {len(failed)}")

    if verbose:
        print(f"[kline_em] 批量完成 {len(results)}/{len(stocks)}，失败 {len(failed)}")
    return results
