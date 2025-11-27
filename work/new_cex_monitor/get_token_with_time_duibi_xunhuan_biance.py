import time
import traceback
import os
from datetime import datetime

# === 全局心跳配置 ===
HEARTBEAT_INTERVAL = 8 * 60 * 60   # 8 小时
POLL_INTERVAL = 30 * 60            # 30 分钟
LAST_HEARTBEAT_TS = 0              # 进程级变量，记录最近一次心跳发送时间戳

# === Telegram 安全发送工具 ===
def escape_markdown_v2(text: str) -> str:
    # 如果你的 tgbot 默认 parse_mode=MarkdownV2，请转义；若默认纯文本，可不转义
    special_chars = r'_\*\[\]\(\)~`>#+-=|{}\.!'
    for ch in special_chars:
        text = text.replace(ch, '\\' + ch)
    return text

def split_message(text, limit=4000):
    parts = []
    while len(text) > limit:
        split_pos = text.rfind("\n", 0, limit)
        if split_pos == -1:
            split_pos = limit
        parts.append(text[:split_pos])
        text = text[split_pos:]
    parts.append(text)
    return parts

def safe_send_text(tgbot, chat, text, proxy_port, use_markdown_v2=False):
    # 统一处理过长/转义
    send_text = escape_markdown_v2(text) if use_markdown_v2 else text
    for part in split_message(send_text, 4000):
        # 如果 tgbot 支持 parse_mode 参数，且你需要用 MarkdownV2：
        # tgbot.sendmessage_chatid(chat, part, proxy_port, parse_mode="MarkdownV2")
        # 否则走最稳妥的纯文本：
        tgbot.sendmessage_chatid(chat, part, proxy_port)

def main():
    try:
        # === 你的原始导入 ===
        import dexprice.modules.cex.future.cex_getall_token_future as getalltoken
        import dexprice.modules.tg.tgbot as tgbot
        import dexprice.modules.tg.mexctg as mexctg  # 未使用也保留
        import dexprice.modules.utilis.define as define  # 未使用也保留
        import dexprice.modules.cexdb.cexdb as cexdb
        import dexprice.modules.utilis.findroot as findroot
        import dexprice.modules.mexc.initial_timesta as initial_timesta  # 未使用也保留
        import dexprice.modules.cex.future.cex_ovhl as initial_timesta_parall
        import dexprice.modules.proxy.proxymultitheread as proxymultitheread  # 未使用也保留
        import dexprice.modules.cex.future.starttime_bybit as starttime_bybit
        import dexprice.modules.cex.future.starttime_binance as starttime_binance
        import dexprice.modules.cex.future.starttime_bitget as starttime_bitget
        import dexprice.modules.cex.cex_proxy as cex_proxy

        # === 环境初始化 ===
        current_dir = os.path.dirname(os.path.abspath(__file__))
        PROJECT_ROOT = findroot.find_project_root(current_dir)
        DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")
        db_folder = os.path.join(DATA_FOLDER, 'cex', 'new_cex_monitor')

        rate = 0.3
        capacity = 20
        max_threads_per_proxy = 1
        clash_api_url = "http://127.0.0.1:9097"
        headers = {"Authorization": "Bearer manba"}
        startport = 50000

        chat_id = "@jingou24"
        proxy_port = 7890

        # === 一个小工具：跑一个交易所，返回“新增token列表” ===
        def run_one_exchange(cex_name: str, determine_initial_timesta_func):
            db_name = f"{cex_name}_contract.db"
            db = cexdb.CexSQLiteDatabase(db_folder, db_name)

            try:
                db.connect()
                symbol = getalltoken.get_all_token(cex_name, proxy_port)
                proxys = cex_proxy.get_one_ip_proxy_multithread_distinct(
                    startport, clash_api_url, headers, cex_name
                )

                task_manager = initial_timesta_parall.CexTaskManager(
                    symbol,
                    proxys,
                    rate,
                    capacity,
                    max_threads_per_proxy,
                    determine_initial_timesta_func
                )
                results, failed_tasks = task_manager.run()

                # 读库已有 token
                token = db.readdbtoken()

                # 求增量
                result_names = {item.name.strip() for item in results}
                token_names = {item.name.strip() for item in token}
                extra_names = result_names - token_names
                extra_tokens = [item for item in results if item.name.strip() in extra_names]

                # 更新库
                db.insert_Multidata(results)
                return extra_tokens

            finally:
                try:
                    db.close()
                except Exception:
                    pass

        # === 分别跑三家交易所，拿到新增 ===
        binance_extra = run_one_exchange('binance', starttime_binance.determine_initial_timesta)
        bybit_extra   = run_one_exchange('bybit',   starttime_bybit.determine_initial_timesta)
        bitget_extra  = run_one_exchange('bitget',  starttime_bitget.determine_initial_timesta)

        # === 拼消息（仅当有新增时） ===
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        has_updates = any([binance_extra, bybit_extra, bitget_extra])

        if has_updates:
            lines = [f"{now_str} 新增合约列表"]
            lines.append("binance：")
            for tk in binance_extra:
                lines.append(f"  - {tk.name.strip()}")
            lines.append("bybit：")
            for tk in bybit_extra:
                lines.append(f"  - {tk.name.strip()}")
            lines.append("bitget：")
            for tk in bitget_extra:
                lines.append(f"  - {tk.name.strip()}")
            final_message = "\n".join(lines)

            # 发送“增量消息”
            safe_send_text(tgbot, chat_id, final_message, proxy_port, use_markdown_v2=False)
            print("已发送新增消息。")
        else:
            print(f"{now_str} 无新增，跳过发送。")

        # === 心跳：每 8 小时必须发一次“系统正常” ===
        global LAST_HEARTBEAT_TS
        now_ts = time.time()
        if (now_ts - LAST_HEARTBEAT_TS) >= HEARTBEAT_INTERVAL:
            hb_msg = f"{now_str} 心跳：系统正常"
            safe_send_text(tgbot, chat_id, hb_msg, proxy_port, use_markdown_v2=False)
            LAST_HEARTBEAT_TS = now_ts
            print("已发送心跳。")

        print("本轮运行完成。")

    except Exception as e:
        print("运行失败：", e)
        traceback.print_exc()


if __name__ == "__main__":
    print("启动监控：每30分钟检查一次，且每8小时发送一次心跳。")
    while True:
        print(f"\n--- 新一轮执行: {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
        main()
        print("休眠 30 分钟...\n")
        time.sleep(POLL_INTERVAL)  # 30 分钟
