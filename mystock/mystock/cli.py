"""命令行入口，提供标的更新、静态筛选和策略运行。"""
from __future__ import annotations

import argparse
from typing import Iterable

from .db.sqlite_db import StockDB
from .pipeline.run_strategy import run_market_strategy
from .pipeline.screen import screen_market
from .pipeline.update_symbols import update_symbols
from .screener.criteria import StaticCriteria
from .strategy.base import StrategyResult
from .strategy.volume_spike import VolumeSpikeStrategy

DEFAULT_DB_PATH = "Data/stocks.db"


def _split_markets(value: str) -> list[str]:
    """CLI 用逗号传多个市场，保留输入顺序。"""
    return [part.strip() for part in value.split(",") if part.strip()]


def _split_words(value: str | None) -> list[str]:
    """名称排除词用逗号分隔，便于命令行传参。"""
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def _criteria_from_args(args: argparse.Namespace) -> StaticCriteria:
    """把 CLI 参数映射到静态筛选条件。"""
    return StaticCriteria(
        total_mv_min=args.min_mv,
        total_mv_max=args.max_mv,
        circ_mv_min=args.min_circ_mv,
        circ_mv_max=args.max_circ_mv,
        turnover_rate_min=args.min_turnover,
        turnover_rate_max=args.max_turnover,
        pe_ratio_min=args.min_pe,
        pe_ratio_max=args.max_pe,
        pb_ratio_min=args.min_pb,
        pb_ratio_max=args.max_pb,
        price_min=args.min_price,
        price_max=args.max_price,
        amount_min=args.min_amount,
        name_exclude=_split_words(args.exclude_name),
    )


def _has_criteria(c: StaticCriteria) -> bool:
    """strategy 子命令没有筛选参数时不额外缩小范围。"""
    values = c.__dict__.copy()
    return any(value not in (None, []) for value in values.values())


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--db", default=DEFAULT_DB_PATH, help="SQLite 数据库路径")


def _add_criteria_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--min-mv", type=float, default=None, help="总市值下限")
    parser.add_argument("--max-mv", type=float, default=None, help="总市值上限")
    parser.add_argument("--min-circ-mv", type=float, default=None, help="流通市值下限")
    parser.add_argument("--max-circ-mv", type=float, default=None, help="流通市值上限")
    parser.add_argument("--min-turnover", type=float, default=None, help="换手率下限")
    parser.add_argument("--max-turnover", type=float, default=None, help="换手率上限")
    parser.add_argument("--min-pe", type=float, default=None, help="市盈率下限")
    parser.add_argument("--max-pe", type=float, default=None, help="市盈率上限")
    parser.add_argument("--min-pb", type=float, default=None, help="市净率下限")
    parser.add_argument("--max-pb", type=float, default=None, help="市净率上限")
    parser.add_argument("--min-price", type=float, default=None, help="价格下限")
    parser.add_argument("--max-price", type=float, default=None, help="价格上限")
    parser.add_argument("--min-amount", type=float, default=None, help="成交额下限")
    parser.add_argument("--exclude-name", default="", help="名称排除词，逗号分隔")


def _format_ratio(value: object) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.2f}"
    return ""


def _print_stock_table(stocks: Iterable[object]) -> None:
    print(f"{'代码':<12} {'名称':<20} {'价格':>10} {'总市值':>14} {'PE':>10}")
    for stock in stocks:
        print(
            f"{stock.symbol:<12} {stock.name:<20} "
            f"{stock.price if stock.price is not None else '':>10} "
            f"{stock.total_mv if stock.total_mv is not None else '':>14} "
            f"{stock.pe_ratio if stock.pe_ratio is not None else '':>10}"
        )


def _print_strategy_table(
    results: list[StrategyResult],
    names: dict[str, str],
    limit: int,
) -> None:
    print(f"{'代码':<12} {'名称':<20} {'ratio':>10} reason")
    for result in results[:limit]:
        ratio = _format_ratio(result.metrics.get("ratio"))
        print(
            f"{result.symbol:<12} {names.get(result.stock_id, ''):<20} "
            f"{ratio:>10} {result.reason}"
        )


def _cmd_update_symbols(args: argparse.Namespace) -> None:
    counts = update_symbols(
        args.db,
        _split_markets(args.market),
        use_proxy=args.proxy,
        verbose=not args.quiet,
    )
    for market, count in counts.items():
        print(f"{market}: {count}")


def _cmd_screen(args: argparse.Namespace) -> None:
    stocks = screen_market(
        args.db,
        args.market,
        _criteria_from_args(args),
        verbose=not args.quiet,
    )
    _print_stock_table(stocks)


def _cmd_strategy(args: argparse.Namespace) -> None:
    criteria = _criteria_from_args(args)
    strategy = VolumeSpikeStrategy(
        lookback=args.lookback,
        multiple=args.multiple,
        use=args.use,
    )
    results = run_market_strategy(
        args.db,
        args.market,
        strategy,
        criteria=criteria if _has_criteria(criteria) else None,
        start_date=args.start,
        end_date=args.end,
        source=args.source,
        use_proxy=args.proxy,
        max_workers=args.max_workers,
        persist_ohlcv=not args.no_persist,
        verbose=not args.quiet,
    )
    with StockDB(args.db) as db:
        names = {stock.stock_id: stock.name for stock in db.read_stocks(args.market)}
    _print_strategy_table(results, names, args.limit)


def build_parser() -> argparse.ArgumentParser:
    """拆出 parser，便于后续测试 CLI 参数。"""
    parser = argparse.ArgumentParser(prog="mystock")
    subparsers = parser.add_subparsers(dest="command", required=True)

    update_parser = subparsers.add_parser("update-symbols", help="更新标的快照")
    _add_common(update_parser)
    update_parser.add_argument("--market", default="A,US", help="市场，逗号分隔")
    update_parser.add_argument("--proxy", action="store_true", help="启用 clash 代理池")
    update_parser.add_argument("--quiet", action="store_true", help="减少过程输出")
    update_parser.set_defaults(func=_cmd_update_symbols)

    screen_parser = subparsers.add_parser("screen", help="静态筛选")
    _add_common(screen_parser)
    screen_parser.add_argument("--market", default="A", help="市场")
    screen_parser.add_argument("--quiet", action="store_true", help="减少过程输出")
    _add_criteria_args(screen_parser)
    screen_parser.set_defaults(func=_cmd_screen)

    strategy_parser = subparsers.add_parser("strategy", help="运行放量策略")
    _add_common(strategy_parser)
    strategy_parser.add_argument("--market", default="A", help="市场")
    strategy_parser.add_argument("--lookback", type=int, default=10, help="回看天数")
    strategy_parser.add_argument("--multiple", type=float, default=10.0, help="放量倍数")
    strategy_parser.add_argument("--use", choices=("volume", "amount"), default="volume", help="使用成交量或成交额")
    strategy_parser.add_argument("--source", choices=("yahoo", "eastmoney"), default="yahoo", help="OHLCV数据源：yahoo(走clash绕限流) / eastmoney(国内直连)")
    strategy_parser.add_argument("--start", default="20240101", help="开始日期，格式 YYYYMMDD")
    strategy_parser.add_argument("--end", default="20300101", help="结束日期，格式 YYYYMMDD")
    strategy_parser.add_argument("--proxy", action="store_true", help="启用 clash 代理池")
    strategy_parser.add_argument("--limit", type=int, default=30, help="最多打印结果数")
    strategy_parser.add_argument("--max-workers", type=int, default=8, help="K线并发数")
    strategy_parser.add_argument("--no-persist", action="store_true", help="不写入 K线数据库")
    strategy_parser.add_argument("--quiet", action="store_true", help="减少过程输出")
    _add_criteria_args(strategy_parser)
    strategy_parser.set_defaults(func=_cmd_strategy)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

