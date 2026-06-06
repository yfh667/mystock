# mystock

`mystock` 是一个 A 股/美股行情数据系统，由原 crypto 数据项目转型而来。底层负责东方财富数据源、模型和 SQLite 存储；上层提供静态筛选、策略运行和命令行编排。

## 安装

```bash
pip install -r requirements.txt
```

## 核心用法

更新 A 股和美股标的快照：

```bash
python -m mystock.cli update-symbols --market A,US
```

按静态指标筛选：

```bash
python -m mystock.cli screen --market A --min-mv 1e10 --max-pe 30 --exclude-name ST,退
```

运行放量策略：

```bash
python -m mystock.cli strategy --market A --source yahoo --lookback 10 --multiple 10 --start 20240101 --end 20241231 --limit 30
```

如需指定数据库路径，三个命令都可加：

```bash
--db Data/stocks.db
```

## 目录结构

```text
mystock/
  datasource/    东财快照(eastmoney)、东财K线(kline_em)、Yahoo K线(yahoo)、代理池(proxy_pool)
  db/            SQLite 存储
  screener/      静态指标筛选
  strategy/      策略接口、放量策略和批量 runner
  pipeline/      更新、筛选、策略运行编排
  cli.py         命令行入口
```

## 数据源策略（重要）

系统用两个数据源，各取所长：

| 用途 | 数据源 | 网络 | 说明 |
|---|---|---|---|
| 标的列表 + 静态指标(市值/PE/换手) | 东方财富 | 国内**直连** | 指标变化慢，低频更新（每天1次不会被限流） |
| OHLCV 日K（策略用，高频/批量） | **Yahoo Finance** | 走 **clash 代理池** | 绕开东财 IP 限流，同时覆盖 A股/美股/港股 |

**为什么这样分**：东方财富按 IP 限流，密集请求会被整站封数十分钟；而 clash 是翻墙(国外)节点，访问东财(国内)成功率低，但访问 Yahoo(国外)非常稳定。所以**列表/指标走东财直连，K线走 Yahoo+clash**。

运行策略时 `--source` 默认 `yahoo`（自动走 clash 代理池，无需加 `--proxy`）：

```bash
# 推荐：Yahoo 走 clash，绕开东财限流
python -m mystock.cli strategy --market A --source yahoo --lookback 10 --multiple 10

# 备选：东财国内直连（量大易被限流）
python -m mystock.cli strategy --market A --source eastmoney --proxy
```

标的更新被限流时，也可对东财启用代理池兜底（但国外节点对东财成功率低，更建议降低频率）：

```bash
python -m mystock.cli update-symbols --market A --proxy
```

代理池探活 `127.0.0.1:50000` 起的本地端口：Yahoo 用 google 探活筛翻墙节点，东财用东财接口探活。`config.disable_system_proxy()` 会在管线入口自动调用（本机有系统代理时绕过它直连国内源）。

## 一键真实冒烟测试

```bash
python scripts/smoke_test.py --proxy   # 拉标的→筛选→拉K线→跑策略
```

