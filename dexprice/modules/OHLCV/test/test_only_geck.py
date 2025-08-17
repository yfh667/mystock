# -*- coding: utf-8 -*-
"""
GeckoTerminal OHLCV fetcher
- Endpoint: /api/v2/networks/{network}/pools/{pool_address}/ohlcv/{timeframe}
- Docs: https://www.geckoterminal.com/dex-api  (see API Guide & Swagger)
"""

from __future__ import annotations
import time
import requests
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta, timezone

GT_ROOT = "https://api.geckoterminal.com/api/v2"

# 官方说明的 timeframe 与可用 aggregate 取值（minute: 1/5/15；hour: 1/4/12；day: 1）
TIMEFRAME_ALLOWED = {
    "minute": {1, 5, 15},
    "hour": {1, 4, 12},
    "day": {1},
}


class GeckoTerminalError(Exception):
    pass


def _validate_params(
        network: str,
        pool_address: str,
        timeframe: str,
        aggregate: int,
        limit: int,
        currency: str,
        token: str,
        before_timestamp: Optional[int],
) -> None:
    if not isinstance(network, str) or not network:
        raise ValueError("network must be a non-empty string, e.g. 'bsc'.")

    if not isinstance(pool_address, str) or not pool_address.startswith("0x"):
        # 这里以 EVM 示例校验，非 EVM 链可按需放宽
        raise ValueError("pool_address must be the pool (pair) address string, e.g. '0x...'.")

    timeframe = timeframe.lower()
    if timeframe not in TIMEFRAME_ALLOWED:
        raise ValueError("timeframe must be one of {'minute','hour','day'}.")

    if aggregate not in TIMEFRAME_ALLOWED[timeframe]:
        raise ValueError(f"aggregate={aggregate} is invalid for timeframe='{timeframe}'. "
                         f"Allowed: {sorted(TIMEFRAME_ALLOWED[timeframe])}.")

    if not (1 <= limit <= 1000):
        # 文档未显式给出上限；这里做个宽松保护
        raise ValueError("limit must be in [1, 1000].")

    if currency.lower() not in {"usd"}:
        # 当前公开文档主要示例为 usd；预留扩展
        raise ValueError("currency currently supports 'usd' in public examples.")

    if token.lower() not in {"base"}:
        # 文档里常见示例是 token=base
        raise ValueError("token must be 'base' (price in base token) per public endpoint examples.")

    if before_timestamp is not None and before_timestamp <= 0:
        raise ValueError("before_timestamp must be a positive unix timestamp in seconds.")


def _build_ohlcv_url(network: str, pool_address: str, timeframe: str) -> str:
    return f"{GT_ROOT}/networks/{network}/pools/{pool_address}/ohlcv/{timeframe}"


def get_ohlcv_data_with_proxy(
        network: str,
        pool_address: str,
        timeframe: str,
        aggregate: int = 1,
        *,
        before_timestamp: Optional[int] = None,
        limit: int = 100,
        currency: str = "usd",
        token: str = "base",
        proxy_port: Optional[int] = None,
        max_retries: int = 5,
        timeout: int = 10,
        backoff_base: float = 2.0,
) -> Dict[str, Any]:
    """
    拉取 GeckoTerminal OHLCV 数据。返回结构包含：
      - raw: 原始 JSON
      - ohlcv_rows: 原始数组形式 [[ts, o, h, l, c, v], ...]
      - ohlcv: 结构化后的列表[{'ts':..., 'time_utc':..., 'o':..., 'h':..., 'l':..., 'c':..., 'v':...}, ...]
      - meta: 附带的元信息（network/pool/timeframe/aggregate/limit/before_timestamp）
    """
    _validate_params(network, pool_address, timeframe, aggregate, limit, currency, token, before_timestamp)

    url = _build_ohlcv_url(network, pool_address, timeframe)
    params = {
        "aggregate": str(aggregate),
        "limit": str(limit),
        "currency": currency,
        "token": token,
    }
    if before_timestamp is not None:
        params["before_timestamp"] = str(before_timestamp)

    proxies = None
    if proxy_port:
        proxy_url = f"http://127.0.0.1:{proxy_port}"
        proxies = {"http": proxy_url, "https": proxy_url}

    attempt = 0
    last_exc: Optional[Exception] = None

    while attempt < max_retries:
        try:
            resp = requests.get(url, params=params, proxies=proxies, timeout=timeout)
            if resp.status_code == 200:
                raw = resp.json()
                # 解析 data.attributes.ohlcv_list => [[ts, o, h, l, c, v], ...]
                try:
                    attrs = raw["data"]["attributes"]
                    rows = attrs.get("ohlcv_list") or attrs.get("ohlcv") or []
                except (TypeError, KeyError):
                    rows = []

                # 结构化
                parsed: List[Dict[str, Any]] = []
                for row in rows:
                    # 规范是 [timestamp, open, high, low, close, volume]
                    if not isinstance(row, (list, tuple)) or len(row) < 6:
                        continue
                    ts, o, h, l, c, v = row[:6]
                    try:
                        ts_int = int(ts)
                    except Exception:
                        # 某些情况下后端也可能返回字符串
                        ts_int = int(float(ts))
                    parsed.append({
                        "ts": ts_int,
                        "time_utc": datetime.fromtimestamp(ts_int, tz=timezone.utc).isoformat(),
                        "o": float(o),
                        "h": float(h),
                        "l": float(l),
                        "c": float(c),
                        "v": float(v),
                    })

                return {
                    "raw": raw,
                    "ohlcv_rows": rows,
                    "ohlcv": parsed,
                    "meta": {
                        "network": network,
                        "pool_address": pool_address,
                        "timeframe": timeframe,
                        "aggregate": aggregate,
                        "limit": limit,
                        "currency": currency,
                        "token": token,
                        "before_timestamp": before_timestamp,
                        "used_proxy": bool(proxies),
                    },
                }

            elif resp.status_code == 404:
                # 池子或网络不存在时就会 404：直接返回空
                return {
                    "raw": None,
                    "ohlcv_rows": [],
                    "ohlcv": [],
                    "meta": {
                        "network": network,
                        "pool_address": pool_address,
                        "timeframe": timeframe,
                        "aggregate": aggregate,
                        "limit": limit,
                        "currency": currency,
                        "token": token,
                        "before_timestamp": before_timestamp,
                        "used_proxy": bool(proxies),
                        "note": "HTTP 404 Not Found",
                    },
                }
            elif resp.status_code == 429:
                # 速率受限：退避等待（公开接口通常有速率限制）
                sleep_s = 5 if attempt == 0 else min(60, backoff_base ** attempt)
                time.sleep(sleep_s)
            elif 500 <= resp.status_code < 600:
                # 服务端错误：退避重试
                sleep_s = min(60, backoff_base ** attempt)
                time.sleep(sleep_s)
            else:
                # 其他状态码：抛出
                raise GeckoTerminalError(f"HTTP {resp.status_code}: {resp.text[:200]}")
        except requests.RequestException as e:
            last_exc = e
            sleep_s = min(60, backoff_base ** attempt)
            time.sleep(sleep_s)
        finally:
            attempt += 1

    # 超过最大重试
    if last_exc:
        raise GeckoTerminalError(f"Request failed after {max_retries} attempts: {last_exc}")
    raise GeckoTerminalError(f"Request failed after {max_retries} attempts with no response.")


# ---------- 小工具：把“若干天前”转 before_timestamp ----------
def days_ago_timestamp(days: int, *, tz: timezone = timezone.utc) -> int:
    now = datetime.now(tz=tz)
    ts = int((now - timedelta(days=days)).timestamp())
    return ts


if __name__ == "__main__":
    # ===== 你的 DEMO 场景 =====
    # chainid = bsc
    network = "bsc"
    # pair (pool) address
    pair_address = "0x7cCC3010e52fbca54467ff68eEc4be78420571C5"

    # 你给的 token 示例元信息（仅打印，非 API 所需）
    token_meta = dict(
        address="0xE3225e11Cab122F1a126A28997788E5230838ab9",
        name="XNY",
        price_usd=0.02138,
        liquidity_usd=2_778_966.77,
        fdv=213_876_273.0,
        pair_address=pair_address,
    )
    print("[Token Meta]", token_meta)

    # 拉 5 分钟 K 线，向后取 10 根，从 150 天前往前切一段（before_timestamp 表示“在此时间之前”的最后 N 根）
    timeframe = "day"  # "minute" | "hour" | "day"
    aggregate = 1  # minute: 1/5/15；hour: 1/4/12；day: 1
    limit = 100
    before_ts = days_ago_timestamp(150)
    print("Before timestamp:", before_ts, datetime.fromtimestamp(before_ts, tz=timezone.utc))
    current_timestamp = int(time.time())

    result = get_ohlcv_data_with_proxy(
        network=network,
        pool_address=pair_address,
        timeframe=timeframe,
        aggregate=aggregate,
        before_timestamp=current_timestamp,
        limit=limit,
        currency="usd",
        token="base",
        proxy_port=7890,  # 如需本地代理，改成端口号，如 50005
    )

    # 打印结构化 K 线
    ohlcv = result["ohlcv"]
    print(f"Fetched {len(ohlcv)} candles")
    for row in ohlcv:
        print(f"{row['ts']} | {row['time_utc']} | O={row['o']} H={row['h']} L={row['l']} C={row['c']} V={row['v']}")
