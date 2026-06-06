"""真实数据冒烟测试 —— 一键验证 A股全链路。

用法（在 mystock 包根目录）：
    python scripts/smoke_test.py            # 本机直连
    python scripts/smoke_test.py --proxy    # 走 clash 代理池（本机被限流时用）

流程：拉 A股标的入库 -> 静态筛选 -> 对命中前 N 只拉日K -> 跑放量策略。
"""
from __future__ import annotations

import argparse
import os
import sys

# 允许直接 python scripts/smoke_test.py 运行
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mystock.config import Market, disable_system_proxy
from mystock.datasource import kline_em
from mystock.datasource.eastmoney import fetch_snapshot
from mystock.datasource.proxy_pool import ProxyPool
from mystock.db.sqlite_db import StockDB
from mystock.screener.criteria import StaticCriteria
from mystock.screener.static_screener import screen
from mystock.strategy.runner import run_strategy
from mystock.strategy.volume_spike import VolumeSpikeStrategy


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--proxy", action="store_true", help="启用 clash 代理池")
    ap.add_argument("--db", default="Data/smoke.db")
    ap.add_argument("--topn", type=int, default=20, help="对筛选后前 N 只跑策略")
    args = ap.parse_args()

    disable_system_proxy()
    pool = None
    if args.proxy:
        pool = ProxyPool()
        pool.probe(verbose=True)
        if len(pool) == 0:
            print("⚠ 代理池无可用出口，改用本机直连")
            pool = None

    os.makedirs(os.path.dirname(args.db) or ".", exist_ok=True)

    # 1) 标的
    print("① 拉 A股标的快照 ...")
    stocks = fetch_snapshot(Market.A_SHARE, proxy_pool=pool, verbose=True)
    with StockDB(args.db) as db:
        db.upsert_stocks(stocks)
        print(f"   入库 {len(stocks)} 只")

        # 2) 静态筛选：中大盘、PE 合理、剔除 ST/退
        crit = StaticCriteria(total_mv_min=5e10, pe_ratio_min=0, pe_ratio_max=60,
                              name_exclude=["ST", "退"])
        hit = screen(db.read_stocks(Market.A_SHARE), crit)
        print(f"② 静态筛选命中 {len(hit)} 只（总市值>500亿 且 0<PE<60 且 非ST）")

        # 3) 策略：对命中前 N 只拉日K，跑放量策略
        targets = hit[: args.topn]
        print(f"③ 对前 {len(targets)} 只拉日K，跑放量策略(当日量>过去10日均量×3) ...")
        ohlcv_map = kline_em.fetch_ohlcv_batch(
            targets, start_date="20240601", end_date="20300101",
            proxy_pool=pool, max_workers=6, verbose=True,
        )
        db.upsert_ohlcv([b for g in ohlcv_map.values() for b in g])

    results = run_strategy(targets, ohlcv_map, VolumeSpikeStrategy(lookback=10, multiple=3))
    print(f"   策略命中 {len(results)} 只：")
    for r in results[:30]:
        print(f"   {r.symbol}  放大 {r.metrics['ratio']:.2f} 倍  {r.reason}")
    print("=== 冒烟测试完成 ===")


if __name__ == "__main__":
    main()
