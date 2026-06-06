"""筛选"近一个月创历史新高"的 A 股。

原则：近一个月（recent_days 个交易日）的最高价 >= 此前全部历史最高价，
即历史最高点出现在最近一个月内。

数据：标的列表用东财(直连)，K线用 Yahoo(走 clash 代理池，绕东财限流)。

用法（在 mystock 包根目录）：
    # 全市场（先确保已 update-symbols 入库标的；很慢，建议配 --limit 试跑）
    python scripts/screen_new_high.py --limit 200

    # 指定一批代码快速试跑（无需 update-symbols）
    python scripts/screen_new_high.py --codes 600519,300750,002594,601127

    # 只看近 30 个月内的新高（而非全历史）
    python scripts/screen_new_high.py --limit 200 --history-months 30
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mystock.config import Market, disable_system_proxy
from mystock.datasource import yahoo, kline_em, sina
from mystock.datasource.proxy_pool import ProxyPool
from mystock.db.sqlite_db import StockDB
from mystock.models import Stock
from mystock.strategy.historical_high import HistoricalHighStrategy
from mystock.strategy.runner import run_strategy


def _load_stocks(args) -> list[Stock]:
    """标的来源：--codes 优先；否则读 db；db 空则尝试东财直连拉一次。"""
    if args.codes:
        codes = [c.strip() for c in args.codes.split(",") if c.strip()]
        return [Stock(symbol=c, name=c, market=Market.A_SHARE) for c in codes]

    with StockDB(args.db) as db:
        stocks = db.read_stocks(Market.A_SHARE)
        if stocks:
            return stocks
        print("[标的] 数据库为空，从新浪直连拉取全 A 股列表 ...")
        try:
            stocks = sina.fetch_a_share_list(verbose=True)
            db.upsert_stocks(stocks)
            print(f"[标的] 入库 {len(stocks)} 只")
            return stocks
        except Exception as e:  # noqa: BLE001
            print(f"[标的] 新浪拉取失败：{e!r}")
            print("       可用 --codes 600519,300750 指定代码试跑。")
            return []


def main() -> None:
    ap = argparse.ArgumentParser(description="筛选近一个月创历史新高的 A 股")
    ap.add_argument("--db", default="Data/stocks.db")
    ap.add_argument("--codes", default="", help="指定代码(逗号分隔)，给定则不读库")
    ap.add_argument("--limit", type=int, default=None, help="只跑前 N 只(全市场很慢)")
    ap.add_argument("--recent-days", type=int, default=22, help='"近一个月"的交易日数')
    ap.add_argument("--history-months", type=int, default=None,
                    help="只把近 N 个月算作历史；缺省=全部历史(真历史新高)")
    ap.add_argument("--use", choices=("high", "close"), default="high",
                    help="按最高价或收盘价判定")
    ap.add_argument("--source", choices=("yahoo", "eastmoney"), default="yahoo",
                    help="K线源：yahoo(走clash,未复权) / eastmoney(直连,前复权更准但易限流)")
    ap.add_argument("--start", default="20050101", help="全历史模式下的起始日 YYYYMMDD")
    ap.add_argument("--max-workers", type=int, default=8)
    ap.add_argument("--output", default=None,
                    help="结果保存路径；缺省自动写 Data/new_high_<日期时间>.txt")
    args = ap.parse_args()

    disable_system_proxy()
    stocks = _load_stocks(args)
    if not stocks:
        return
    if args.limit:
        stocks = stocks[: args.limit]
    print(f"[筛选] 待检查 {len(stocks)} 只 A 股")

    # 历史范围：history-months 给定则从那时算起，否则用 --start（很早=全历史）
    if args.history_months:
        start_dt = datetime.now() - timedelta(days=int(args.history_months * 30.5))
        start_date = start_dt.strftime("%Y%m%d")
    else:
        start_date = args.start
    end_date = "20300101"
    print(f"[筛选] 历史范围 {start_date} ~ 今，近一个月={args.recent_days}个交易日，依据={args.use}")

    # 选择 K线源：yahoo 走 clash 代理池(未复权)；eastmoney 直连(前复权更准)
    if args.source == "yahoo":
        kline_mod = yahoo
        pool = ProxyPool()
        pool.probe(target="google", verbose=True)
        if len(pool) == 0:
            print("[警告] 无可用翻墙节点，Yahoo 可能拉取失败")
        print("[提示] Yahoo 已按 adjclose 复权(后复权)，创新高判定与前复权结论一致")
    else:
        kline_mod = kline_em       # 东财 K线默认前复权(fqt=1)
        pool = None                # 国内直连；若限流可改走代理但国外节点成功率低
        print("[提示] 东财前复权，结果更准，但全市场量大易触发 IP 限流")

    ohlcv_map = kline_mod.fetch_ohlcv_batch(
        stocks, start_date=start_date, end_date=end_date,
        proxy_pool=pool, max_workers=args.max_workers, verbose=True,
    )

    strategy = HistoricalHighStrategy(recent_days=args.recent_days, use=args.use)
    results = run_strategy(stocks, ohlcv_map, strategy)
    # 按"突破幅度"降序（ratio>=1 即创新高；越大说明越强势）
    results.sort(key=lambda r: r.metrics.get("ratio", 0), reverse=True)

    names = {s.stock_id: s.name for s in stocks}

    # 组装结果文本（同时用于打印和写文件）
    header = [
        f"# 近一个月创历史新高 A股筛选结果",
        f"# 生成时间: {datetime.now():%Y-%m-%d %H:%M:%S}",
        f"# 参数: recent_days={args.recent_days}  use={args.use}  source={args.source}  "
        f"history={'近%d月'%args.history_months if args.history_months else '全历史'}",
        f"# 检查 {len(stocks)} 只，命中 {len(results)} 只",
        f"{'代码':<10}{'名称':<12}{'历史最高':>12}{'近月最高':>12}{'创新高日':>14}",
    ]
    body = []
    for r in results:
        m = r.metrics
        body.append(
            f"{r.symbol:<10}{names.get(r.stock_id, ''):<12}"
            f"{m['prior_high']:>12.2f}{m['recent_high']:>12.2f}{str(m['peak_day']):>14}"
        )
    text = "\n".join(header + body)
    print("\n" + text)

    # 保存到 txt（留存运行结果）
    out_path = args.output or os.path.join(
        "Data", f"new_high_{datetime.now():%Y%m%d_%H%M%S}.txt"
    )
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(f"\n[已保存] {out_path}")


if __name__ == "__main__":
    main()
