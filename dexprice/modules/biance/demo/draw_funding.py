import dexprice.modules.biance.get_funding_rate as get_funding_rate

import requests
from datetime import datetime, timezone
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates




def plot_funding_rate(funding_data: list[dict], symbol: str):
    """
    将获取到的历史资金费率绘制成阶梯图
    """
    if not funding_data:
        print("没有数据可供绘制！")
        return

    # 1. 将数据转换为 Pandas DataFrame，方便处理
    df = pd.DataFrame(funding_data)

    # 2. 数据类型转换
    # 资金费率转为 float，并乘以 100 转为百分比
    df['fundingRate'] = df['fundingRate'].astype(float) * 100
    # 时间戳转换为可读的 datetime 对象
    df['fundingTime'] = pd.to_datetime(df['fundingTime'], unit='ms')

    # 3. 开始绘图
    plt.figure(figsize=(14, 6))  # 设置画布大小

    # 画阶梯图: drawstyle='steps-post' 代表当前点向右水平延伸直到下一个点
    plt.plot(
        df['fundingTime'],
        df['fundingRate'],
        drawstyle='steps-post',
        color='#1f77b4',
        linewidth=1.5,
        label=f'{symbol} Funding Rate'
    )

    # 4. 添加 0 轴基准线 (非常重要，用来区分多头交费还是空头交费)
    plt.axhline(0, color='red', linestyle='--', linewidth=1, alpha=0.8, label='Zero Line (0%)')

    # 5. 图表修饰
    plt.title(f'{symbol} 资金费率历史走势 (Funding Rate Over Time)', fontsize=14, pad=15)
    plt.xlabel('时间 (UTC)', fontsize=12)
    plt.ylabel('资金费率 (%)', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.legend(loc='upper left')

    # 自动格式化 X 轴的时间显示，防止日期文字重叠
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.gcf().autofmt_xdate()

    # 6. 显示与保存
    # plt.savefig(f"{symbol}_funding_rate.png", dpi=300, bbox_inches='tight') # 如果需要保存成图片取消这行注释
    plt.show()


# === 测试代码 ===
if __name__ == "__main__":
    print("=== 开始获取并绘制 Binance 历史资金费率 ===")

    test_symbol = "ENSO_USDT"

    # 拉取 2 个月的数据（比如2024年初的多头大行情阶段），这样看折线变化比较明显
    start_dt = datetime(2026, 2, 22, tzinfo=timezone.utc)
    end_dt = datetime(2026, 2, 26, tzinfo=timezone.utc)

    funding_rates = get_funding_rate.get_binance_funding_rate(
        symbol=test_symbol,
        start=int(start_dt.timestamp()),
        end=int(end_dt.timestamp()),
        limit=1000,
        port=7890
    )

    if funding_rates:
        print(f"✅ 成功获取到 {len(funding_rates)} 条记录，正在生成图表...")

        # 传入数据进行绘图
        plot_funding_rate(funding_rates, test_symbol)