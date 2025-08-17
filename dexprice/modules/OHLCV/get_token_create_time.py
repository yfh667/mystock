import time
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List

# 复用你已有的：
from dexprice.modules.OHLCV.geck import get_ohlcv_data_with_proxy

def _extract_first_ts(ohlcv_payload: Optional[Dict[str, Any]]) -> Optional[int]:
    """从 Gecko ohlcv 响应里提取第一根 K 线的时间戳。"""
    if not ohlcv_payload:
        return None
    try:
        rows: List[List] = ohlcv_payload["data"]["attributes"]["ohlcv_list"]
        if not rows:
            return None
        return int(rows[0][0])
    except Exception:
        return None

def get_pool_createtime_with_150d_cap(
    network: str,
    pool_address: str,            # 这里传字符串地址；内部会按你的函数要求转成 [addr]
    *,
    proxy_port: Optional[int] = None,
    max_hops: int = 4096
) -> Optional[Dict[str, Any]]:
    """
    通过 Gecko 日线回溯近似获取池子创建时间。
    - 若未触及 150 天限制：返回最早一根日线的 ts（接近创建/首成交时间）。
    - 若触及 150 天限制：返回“现在-150 天”的截点 ts，并标记 is_lower_bound=True。
    返回:
        {
          "ts": <int>,             # 秒级时间戳
          "time_utc": <str>,       # "YYYY-MM-DD HH:MM:SS"
          "is_lower_bound": <bool> # 是否为 150 天的下界
        }
    """
    timeframe = "day"
    aggregate = "1"      # day 只能 1
    limit = 1
    currency = "usd"
    token = "base"

    now = int(time.time())
    cutoff_ts = int((datetime.fromtimestamp(now, tz=timezone.utc) - timedelta(days=150)).timestamp())

    before_ts = now
    earliest_ts: Optional[int] = None

    for _ in range(max_hops):
        payload = get_ohlcv_data_with_proxy(
            network=network,
            pool_address=[pool_address],  # 你的函数体里用 pool_address[0]，所以这里传 list
            timeframe=timeframe,
            aggregate=aggregate,
            before_timestamp=str(before_ts),  # 你的函数接受 str/int 都行
            limit=limit,
            currency=currency,
            token=token,
            proxy_port=proxy_port
        )

        first_ts = _extract_first_ts(payload)
        if first_ts is None:
            # 没有更早数据 -> 可能已经到最早；看当前 earliest_ts 是否已跨过 150 天
            if earliest_ts is None:
                return None  # 连一根都没拿到
            if earliest_ts <= cutoff_ts:
                return {
                    "ts": cutoff_ts,
                    "time_utc": datetime.fromtimestamp(cutoff_ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                    "is_lower_bound": True
                }
            # 没到 150 天，就用拿到的 earliest_ts
            return {
                "ts": earliest_ts,
                "time_utc": datetime.fromtimestamp(earliest_ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                "is_lower_bound": False
            }

        earliest_ts = first_ts

        # 若已达到或穿过 150 天截点，直接以 150 天为下界返回
        if earliest_ts <= cutoff_ts:
            return {
                "ts": cutoff_ts,
                "time_utc": datetime.fromtimestamp(cutoff_ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                "is_lower_bound": True
            }

        # 继续往更早翻页
        before_ts = first_ts - 1

    # 安全兜底：超出 hop 数
    if earliest_ts is not None:
        # 判断是否触及 150 天
        is_lb = earliest_ts <= cutoff_ts
        ts_ret = cutoff_ts if is_lb else earliest_ts
        return {
            "ts": ts_ret,
            "time_utc": datetime.fromtimestamp(ts_ret, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "is_lower_bound": is_lb
        }
    return None
