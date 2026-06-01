import dexprice.modules.biance.get_funding_rate as get_funding_rate
import dexprice.modules.biance.ovhl_binance as ovhl_binance

import requests
from datetime import datetime, timezone
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_combined_chart(funding_data: list[dict], kline_data: list[list], symbol: str):
    """
    将获取到的历史资金费率和 K 线数据绘制在一张图表上 (双 Y 轴)
    """
    if not funding_data or not kline_data:
        print("没有数据可供绘制！")
        return

    # 1. 将数据转换为 Pandas DataFrame，方便处理资金费率
    df_funding = pd.DataFrame(funding_data)
    df_funding['fundingRate'] = df_funding['fundingRate'].astype(float) * 100
    df_funding['fundingTime'] = pd.to_datetime(df_funding['fundingTime'], unit='ms')

    # 2. 将 K 线列表转换为 DataFrame，方便处理 K 线
    df_kline = pd.DataFrame(kline_data,
                            columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av',
                                     'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
    df_kline['time'] = pd.to_datetime(df_kline['time'], unit='ms')
    for col in ['open', 'high', 'low', 'close']:
        df_kline[col] = df_kline[col].astype(float)

    # 3. 开始绘图
    fig, ax1 = plt.subplots(figsize=(14, 8))

    # === 绘制 K 线 (左侧 Y 轴) ===
    up = df_kline[df_kline.close >= df_kline.open]
    down = df_kline[df_kline.close < df_kline.open]
    color_up = 'green'
    color_down = 'red'

    # 动态计算 K 线宽度 (基于数据的时间间隔设定体宽，比如 1H 就是大约 0.03 天)
    time_diff = df_kline['time'].diff().median()
    width_days = time_diff.total_seconds() / 86400 * 0.8 if pd.notnull(time_diff) else 0.03

    # 影线
    ax1.vlines(up.time, up.low, up.high, color=color_up, linewidth=1)
    ax1.vlines(down.time, down.low, down.high, color=color_down, linewidth=1)

    # 实体
    ax1.bar(up.time, up.close - up.open, bottom=up.open, color=color_up, width=width_days, align='center', alpha=0.8,
            label='K 线 (涨)')
    ax1.bar(down.time, down.open - down.close, bottom=down.close, color=color_down, width=width_days, align='center',
            alpha=0.8, label='K 线 (跌)')

    ax1.set_xlabel('时间 (UTC)', fontsize=12)
    ax1.set_ylabel('价格 (USDT)', fontsize=12, color='black')
    ax1.tick_params(axis='y', labelcolor='black')

    # === 绘制资金费率 (右侧 Y 轴) ===
    ax2 = ax1.twinx()
    ax2.plot(
        df_funding['fundingTime'],
        df_funding['fundingRate'],
        drawstyle='steps-post',
        color='#1f77b4',
        linewidth=1.5,
        label=f'{symbol} Funding Rate'
    )

    # 添加 0 轴基准线 (非常重要，用来区分多头交费还是空头交费)
    ax2.axhline(0, color='orange', linestyle='--', linewidth=1.2, alpha=0.8, label='Zero Line (0%)')

    ax2.set_ylabel('资金费率 (%)', fontsize=12, color='#1f77b4')
    ax2.tick_params(axis='y', labelcolor='#1f77b4')

    # 4. 图表修饰
    plt.title(f'{symbol} K 线及资金费率历史走势', fontsize=16, pad=20)
    plt.grid(axis='y', linestyle='--', alpha=0.3)

    # 合并左轴和右轴的图例
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

    # 自动格式化 X 轴的时间显示，防止日期文字重叠
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    fig.autofmt_xdate()

    # 5. 显示与保存
    # plt.savefig(f"{symbol}_kline_funding.png", dpi=300, bbox_inches='tight') # 如果需要保存成图片取消这行注释
    plt.show()


# === 测试代码 ===
if __name__ == "__main__":
    print("=== 开始获取并绘制 Binance 历史资金费率和 K 线 ===")

    test_symbol = "BANANAS31_USDT"

    # 拉取 2 个月的数据（比如2024年初的多头大行情阶段），这样看折线变化比较明显
    start_dt = datetime(2026, 2, 28, tzinfo=timezone.utc)
    end_dt = datetime(2026, 3, 24,hour=4, tzinfo=timezone.utc)

    start_ts = int(start_dt.timestamp())
    end_ts = int(end_dt.timestamp())

    print("获取资金费率中...")
    funding_rates = get_funding_rate.get_binance_funding_rate(
        symbol=test_symbol,
        start=start_ts,
        end=end_ts,
        limit=1000,
        port=7890
    )

    print("获取 K 线数据中...")
    kline_data = ovhl_binance.get_kline_data(
        symbol=test_symbol,
        interval="1H",
        start=start_ts,
        end=end_ts,
        port=7890,
        limit=1500,
        category="futures"
    )

    if funding_rates and kline_data:
        print(f"✅ 成功获取资金费率 {len(funding_rates)} 条，K 线 {len(kline_data)} 条，正在生成图表...")
        plot_combined_chart(funding_rates, kline_data, test_symbol)
    else:
        print("❌ 数据获取失败，请检查网络或时间返回")