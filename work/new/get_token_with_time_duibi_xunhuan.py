import time
import traceback


def main():
    try:
        # 你原来的逻辑都写在这里
        import dexprice.modules.cex.future.cex_getall_token_future as getalltoken
        # ... 其他导入、计算、处理逻辑

        import dexprice.modules.cex.future.cex_getall_token_future as getalltoken

        import dexprice.modules.tg.tgbot as tgbot
        import dexprice.modules.tg.mexctg as mexctg
        import dexprice.modules.utilis.define as define
        import dexprice.modules.cexdb.cexdb as cexdb

        import dexprice.modules.utilis.define as define
        import os
        import dexprice.modules.utilis.findroot as findroot
        import dexprice.modules.mexc.initial_timesta as initial_timesta
        import dexprice.modules.cex.future.cex_ovhl as initial_timesta_parall
        import dexprice.modules.proxy.proxymultitheread as proxymultitheread
        import dexprice.modules.cex.future.starttime_bybit as starttime_bybit
        import dexprice.modules.cex.future.starttime_binance as starttime_binance

        import dexprice.modules.cex.future.starttime_bitget as starttime_bitget

        import dexprice.modules.cex.future.testforcex as testforcex

        import dexprice.modules.cex.cex_proxy as cex_proxy
        if __name__ == '__main__':

            current_dir = os.path.dirname(os.path.abspath(__file__))
            PROJECT_ROOT = findroot.find_project_root(current_dir)
            DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")

            db_folder = DATA_FOLDER + '/cex/new'  # 数据库存储文件夹
            rate = 0.3
            capacity = 20
            max_threads_per_proxy = 1
            clash_api_url = "http://127.0.0.1:9097"
            headers = {"Authorization": "Bearer manba"}

            startport = 50000

            cex_name = 'binance'
            db_name = cex_name + "_contract" + '.db'  # 数据库文件名
            db = cexdb.CexSQLiteDatabase(db_folder, db_name)

            db.connect()

            symbol = getalltoken.get_all_token(cex_name, 7890)
            # symbol  = ['BTC','SOL']

            proxys = cex_proxy.get_one_ip_proxy_multithread_distinct(startport, clash_api_url, headers, cex_name)

            task_manager = initial_timesta_parall.CexTaskManager(
                symbol,
                proxys,
                rate,
                capacity,
                max_threads_per_proxy,
                starttime_binance.determine_initial_timesta

            )
            results, failed_tasks = task_manager.run()

            # here we need  duibi ,yu
            token = db.readdbtoken()

            # 假设 results 和 token 已经定义为你提供的列表

            # 提取 name 字段
            result_names = {item.name.strip() for item in results}
            token_names = {item.name.strip() for item in token}

            # 找出 result 中多出来的 name
            extra_names = result_names - token_names

            # 输出多出的 token 信息
            biance_extra_tokens = [item for item in results if item.name.strip() in extra_names]

            db.insert_Multidata(results)
            # 打印实例属性
            db.close()

            cex_name = 'bybit'
            db_name = cex_name + "_contract" + '.db'  # 数据库文件名
            db = cexdb.CexSQLiteDatabase(db_folder, db_name)

            db.connect()

            symbol = getalltoken.get_all_token(cex_name, 7890)
            # symbol  = ['BTC','SOL']

            proxys = cex_proxy.get_one_ip_proxy_multithread_distinct(startport, clash_api_url, headers, cex_name)

            task_manager = initial_timesta_parall.CexTaskManager(
                symbol,
                proxys,
                rate,
                capacity,
                max_threads_per_proxy,
                starttime_bybit.determine_initial_timesta

            )
            results, failed_tasks = task_manager.run()
            #  db.insert_Multidata(results)
            # 打印实例属性

            # here we need  duibi ,yu
            token = db.readdbtoken()

            # 假设 results 和 token 已经定义为你提供的列表

            # 提取 name 字段
            result_names = {item.name.strip() for item in results}
            token_names = {item.name.strip() for item in token}

            # 找出 result 中多出来的 name
            extra_names = result_names - token_names

            # 输出多出的 token 信息
            bybit_extra_tokens = [item for item in results if item.name.strip() in extra_names]

            db.close()

            cex_name = 'bitget'
            db_name = cex_name + "_contract" + '.db'  # 数据库文件名
            db = cexdb.CexSQLiteDatabase(db_folder, db_name)

            db.connect()

            symbol = getalltoken.get_all_token(cex_name, 7890)
            # symbol  = ['BTC','SOL']

            proxys = cex_proxy.get_one_ip_proxy_multithread_distinct(startport, clash_api_url, headers, cex_name)

            task_manager = initial_timesta_parall.CexTaskManager(
                symbol,
                proxys,
                rate,
                capacity,
                max_threads_per_proxy,
                starttime_bitget.determine_initial_timesta

            )
            results, failed_tasks = task_manager.run()

            # here we need  duibi ,yu
            token = db.readdbtoken()

            # 假设 results 和 token 已经定义为你提供的列表

            # 提取 name 字段
            result_names = {item.name.strip() for item in results}
            token_names = {item.name.strip() for item in token}

            # 找出 result 中多出来的 name
            extra_names = result_names - token_names

            # 输出多出的 token 信息
            bitget_extra_tokens = [item for item in results if item.name.strip() in extra_names]

            #
            #  db.insert_Multidata(results)
            # 打印实例属性
            db.close()

            # for token in biance_extra_tokens:
            #     print(token)
            #
            #
            # for token in bybit_extra_tokens:
            #     print(token)
            #
            # for token in bitget_extra_tokens:
            #     print(token)

            from datetime import datetime

            # 构建信息内容
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message_lines = [f"{now_str}"]

            # 添加 Binance 增量
            message_lines.append("binance：")
            for token in biance_extra_tokens:
                message_lines.append(f"  - {token.name.strip()}")

            # 添加 Bybit 增量
            message_lines.append("bybit：")
            for token in bybit_extra_tokens:
                message_lines.append(f"  - {token.name.strip()}")

            # 添加 Bitget 增量
            message_lines.append("bitget：")
            for token in bitget_extra_tokens:
                message_lines.append(f"  - {token.name.strip()}")

            # 拼接最终信息
            final_message = "\n".join(message_lines)

            # 发送到 Telegram
            tgbot.sendmessage_chatid("@jingou24", final_message, 7890)

        print("运行成功一次！")
    except Exception as e:
        print("运行失败：", e)
        traceback.print_exc()

if __name__ == "__main__":
    while True:
        print(f"\n--- 新一轮执行: {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
        main()
        print("休眠 8 小时...\n")
        time.sleep(8 * 60 * 60)  # 8 小时