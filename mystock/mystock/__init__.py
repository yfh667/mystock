"""mystock —— A股 / 美股行情数据系统。

由加密货币项目 DexPrice 转型而来，复用其分层架构：
    数据源层(datasource) -> 数据模型(models) -> 存储层(db)
    -> 筛选器(screener) -> 策略引擎(strategy) -> 编排管线(pipeline)

只把"入口"从交易所 API 换成股票数据源（东方财富 / akshare），
其余 OHLCV 模型、SQLite 存储、筛选、策略决策的设计思路与原项目一致。
"""

__version__ = "0.1.0"
