"""SQLite 存储层。

两张表，对标原项目的 token_pairs / price_history：
    stocks         标的表 + 静态指标快照（市值/换手率/市盈率…）
    price_history  日K(OHLCV)，按 (stock_id, time) 去重

stock_id = '市场:代码'（如 'A:600519' / 'US:AAPL'），作为两表关联键。
"""
from __future__ import annotations

import os
import sqlite3
from typing import List, Optional

from ..config import Market
from ..models import Stock, StockOHLCV

# stocks 表里除主键外的指标列，集中定义避免 insert/read 不一致
_STOCK_COLS = [
    "symbol", "name", "market", "raw_code",
    "price", "pct_change", "volume", "amount",
    "turnover_rate", "pe_ratio", "pb_ratio", "total_mv", "circ_mv",
    "list_date",
]


class StockDB:
    """轻量 SQLite 封装。用法：db = StockDB(path); db.connect(); ...; db.close()"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    # ---------- 连接 / 建表 ----------
    def connect(self) -> "StockDB":
        folder = os.path.dirname(os.path.abspath(self.db_path))
        os.makedirs(folder, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
        return self

    def _init_tables(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS stocks (
                stock_id      TEXT PRIMARY KEY,   -- 市场:代码
                symbol        TEXT NOT NULL,
                name          TEXT,
                market        TEXT NOT NULL,
                raw_code      TEXT,
                price         REAL,
                pct_change    REAL,
                volume        REAL,
                amount        REAL,
                turnover_rate REAL,
                pe_ratio      REAL,
                pb_ratio      REAL,
                total_mv      REAL,
                circ_mv       REAL,
                list_date     TEXT,
                updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS price_history (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_id   TEXT NOT NULL,
                symbol     TEXT NOT NULL,
                market     TEXT NOT NULL,
                time       TEXT NOT NULL,
                open       REAL,
                high       REAL,
                low        REAL,
                close      REAL,
                volume     REAL,
                amount     REAL,
                UNIQUE(stock_id, time)
            );
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ph_stock ON price_history(stock_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_stocks_market ON stocks(market);")
        self.conn.commit()

    def close(self) -> None:
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None

    def __enter__(self) -> "StockDB":
        return self.connect()

    def __exit__(self, *exc) -> None:
        self.close()

    # ---------- 标的表 ----------
    def upsert_stocks(self, stocks: List[Stock]) -> int:
        cols = ["stock_id"] + _STOCK_COLS
        placeholders = ",".join("?" for _ in cols)
        updates = ",".join(f"{c}=excluded.{c}" for c in _STOCK_COLS)
        sql = (
            f"INSERT INTO stocks ({','.join(cols)}) VALUES ({placeholders}) "
            f"ON CONFLICT(stock_id) DO UPDATE SET {updates}, updated_at=CURRENT_TIMESTAMP;"
        )
        rows = [
            tuple([s.stock_id] + [getattr(s, c) for c in _STOCK_COLS])
            for s in stocks
        ]
        cur = self.conn.cursor()
        cur.executemany(sql, rows)
        self.conn.commit()
        return len(rows)

    def read_stocks(self, market: Optional[str] = None) -> List[Stock]:
        cur = self.conn.cursor()
        if market:
            cur.execute("SELECT * FROM stocks WHERE market=?;", (market,))
        else:
            cur.execute("SELECT * FROM stocks;")
        out: List[Stock] = []
        for r in cur.fetchall():
            out.append(Stock(
                symbol=r["symbol"], name=r["name"], market=r["market"],
                raw_code=r["raw_code"], price=r["price"], pct_change=r["pct_change"],
                volume=r["volume"], amount=r["amount"], turnover_rate=r["turnover_rate"],
                pe_ratio=r["pe_ratio"], pb_ratio=r["pb_ratio"], total_mv=r["total_mv"],
                circ_mv=r["circ_mv"], list_date=r["list_date"],
            ))
        return out

    # ---------- 日K表 ----------
    def upsert_ohlcv(self, bars: List[StockOHLCV]) -> int:
        sql = """
            INSERT INTO price_history (stock_id, symbol, market, time, open, high, low, close, volume, amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(stock_id, time) DO UPDATE SET
                open=excluded.open, high=excluded.high, low=excluded.low,
                close=excluded.close, volume=excluded.volume, amount=excluded.amount;
        """
        rows = [
            (b.stock_id, b.symbol, b.market, b.time, b.open, b.high, b.low, b.close, b.volume, b.amount)
            for b in bars
        ]
        cur = self.conn.cursor()
        cur.executemany(sql, rows)
        self.conn.commit()
        return len(rows)

    def read_ohlcv(self, symbol: str, market: str) -> List[StockOHLCV]:
        stock_id = f"{market}:{symbol}"
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM price_history WHERE stock_id=? ORDER BY time ASC;", (stock_id,)
        )
        return [
            StockOHLCV(
                symbol=r["symbol"], market=r["market"], time=r["time"],
                open=r["open"], high=r["high"], low=r["low"], close=r["close"],
                volume=r["volume"], amount=r["amount"],
            )
            for r in cur.fetchall()
        ]
