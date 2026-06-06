"""新浪财经 A 股列表数据源（直连）。

东方财富按 IP 限流时，用新浪拿全市场 A 股代码+名称（不同站，国内直连可用）。
只提供标的列表，不含市值/PE 等指标（那些仍可用东财快照低频补充）。
"""
from __future__ import annotations

import json
from typing import List, Sequence

import requests

from ..config import Market
from ..models import Stock

_LIST_URL = (
    "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/"
    "Market_Center.getHQNodeData"
)
_UA = {"User-Agent": "Mozilla/5.0"}


def fetch_a_share_list(
    markets: Sequence[str] = ("sh", "sz"),
    *,
    page_size: int = 100,   # 新浪单页上限 100
    timeout: float = 12.0,
    verbose: bool = False,
) -> List[Stock]:
    """分页拉取全部 A 股代码+名称。

    :param markets: 保留的市场前缀，默认沪('sh')深('sz')；可加 'bj'(北交所)。
                    注意新浪按 symbol 升序，北交所(bj)排最前，需翻过若干页才到沪深。
    :return: Stock 列表（仅 symbol/name/market，指标留空）。
    """
    page_size = min(page_size, 100)
    session = requests.Session()
    session.trust_env = False

    out: List[Stock] = []
    seen = set()
    page = 1
    while True:
        params = {
            "page": page, "num": page_size, "sort": "symbol",
            "asc": 1, "node": "hs_a",
        }
        r = session.get(_LIST_URL, params=params, headers=_UA, timeout=timeout)
        text = r.text.strip()
        if not text or text in ("null", "[]"):
            break
        data = json.loads(text)
        if not data:
            break
        for it in data:
            sym = it.get("symbol", "")      # 形如 sh600519 / sz000001 / bj920000
            prefix = sym[:2]
            if prefix not in markets:
                continue
            code = it.get("code", "")
            if not code or code in seen:
                continue
            seen.add(code)
            out.append(Stock(symbol=code, name=it.get("name", code), market=Market.A_SHARE))
        if verbose:
            print(f"[sina] page {page} 累计 {len(out)}")
        if len(data) < page_size:
            break
        page += 1
    return out
