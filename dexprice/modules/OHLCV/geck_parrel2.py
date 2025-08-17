import dexprice.modules.OHLCV.geck as geck


import threading
import time
import math
from queue import Queue, Empty
from tqdm import tqdm

import threading
from typing import Dict, List
from token_bucket import Limiter, MemoryStorage
import dexprice.modules.proxy.proxydefine as proxydefine


import dexprice.modules.proxy.testproxy as testproxy
import dexprice.modules.OHLCV.one_geck as  one_geck


# 2与1的区别在于，2是用于处理单个地址的，相当于我要知道某个某个地址在一段时间内的。
class GeckTaskManager2:
    def __init__(self, addressesqueues:list[one_geck.addressesqueue],  chain_id, proxies, rate, capacity, max_threads_per_proxy):
        self.task_queue = Queue()
        self.failed_tasks = Queue()
        self.results = []
        self.result_lock = threading.Lock()
        self.batch_size = 1




        self.add_tasks(addressesqueues)


        self.chain_id = chain_id
        self.proxy_pool = proxydefine.ProxyPool(rate, capacity, max_threads_per_proxy)
        #  self.proxy_pool.add_proxy()
        self.proxy_pool.add_proxies(proxies)
        self.progress_lock = threading.Lock()

        self.threads = []
        self.stop_event = threading.Event()
        self.max_threads_per_proxy = max_threads_per_proxy

        # 计算总任务数（批次数量）

        self.total_tasks = math.ceil(len(addressesqueues) / self.batch_size)
        self.progress_bar = tqdm(total=self.total_tasks, desc="GECK2_Total Progress")

    def add_tasks(self, addressesqueues):
        #  batch_size = 30
        # 将地址列表按照 batch_size 切分
        for addressqueue in addressesqueues:
            self.task_queue.put(addressqueue)
    def worker(self, stop_event):
        print(f"Worker thread {threading.current_thread().name} started.")
        while not stop_event.is_set():
            try:
                addressqueue = self.task_queue.get(timeout=1)
                #    print(f"Thread {threading.current_thread().name} processing addresses: {addresses}")
                success =self.process_task(addressqueue)
                if success:
                    self.task_queue.task_done()
                    with self.progress_lock:
                        self.progress_bar.update(1)  # 每完成一个任务，更新进度条
            except Empty:
                if self.task_queue.empty():
                    print(f"Thread {threading.current_thread().name} exiting: task queue is empty.")
                    break
                else:
                    continue



    def run(self):
        threads_lock = threading.Lock()

        # 计算初始线程数
        initial_thread_count = len(self.proxy_pool.get_available_proxies()) * self.max_threads_per_proxy
        monitor_thread = threading.Thread(target=self.monitor_failed_proxies)

        monitor_thread.start()

        # 创建初始线程
        for _ in range(initial_thread_count):
            stop_event = threading.Event()
            thread = threading.Thread(target=self.worker, args=(stop_event,))
            thread.start()
            with threads_lock:
                self.threads.append((thread, stop_event))
        max_retries = 3
        retries = 0
        # 主线程监控代理池和线程数量
        while True:
            # 检查任务队列是否为空
            # if self.task_queue.empty():
            #     break
            if self.task_queue.empty():
                # 检查失败任务队列是否为空
                if not self.failed_tasks.empty() and retries < max_retries:
                    retries += 1
                    print(f"Retrying failed tasks, attempt {retries}")
                    # 将失败的任务重新放回任务队列
                    while not self.failed_tasks.empty():
                        addresses = self.failed_tasks.get()
                        self.task_queue.put(addresses)
                    continue  # 继续主循环，重新处理任务
                else:
                    break  # 任务队列和失败任务队列都为空，或者达到最大重试次数，退出循环

            #  print(f"1 ")
            # 根据可用代理数量调整线程数量
            with self.proxy_pool.lock:
                # print(f"2")

                total_capacity = len(self.proxy_pool.get_all_proxies()) * self.max_threads_per_proxy
            #   print(f"3")

            with threads_lock:
                current_thread_count = len(self.threads)
                if total_capacity > current_thread_count:
                    # 增加线程
                    for _ in range(total_capacity - current_thread_count):
                        stop_event = threading.Event()
                        thread = threading.Thread(target=self.worker, args=(stop_event,))
                        thread.start()
                        self.threads.append((thread, stop_event))
                elif total_capacity < current_thread_count:
                    # 减少线程，通知线程停止
                    threads_to_stop = self.threads[:current_thread_count - total_capacity]
                    for thread, stop_event in threads_to_stop:
                        stop_event.set()  # 通知线程停止
                        thread.join()     # 等待线程结束
                        self.threads.remove((thread, stop_event))

            time.sleep(5)  # 每隔一段时间检查一次

        # 等待剩余的线程完成
        with threads_lock:
            for thread, stop_event in self.threads:
                stop_event.set()
                thread.join()
            self.threads.clear()

        self.progress_bar.close()
        self.stop_event.set()
        monitor_thread.join()
        return self.results, list(self.failed_tasks.queue)

    def process_task(self, addressqueue:one_geck.addressesqueue):
        success = False
        failure_count = 0
        max_failures = 5  # 设置最大失败次数
        proxy_acquired = False  # 记录是否成功获取到代理

        while not success and failure_count < max_failures:
            proxy, limiter, semaphore = self.proxy_pool.acquire_proxy()
            if not proxy:
                print("No available proxies or proxies are at max capacity. Waiting...")
                time.sleep(1)
                continue  # 等待可用代理

            proxy_acquired = True  # 成功获取到代理

            try:
                # 等待速率限制解除
                required_tokens = 1  # 假设每次请求无论批量大小，都只消耗一个令牌
                while not limiter.consume("api_call", required_tokens):
                    time.sleep(0.1)

                # 速率限制允许，进行请求
                tokens_info = geck.get_token_history2(self.chain_id, addressqueue.pool_address, addressqueue.kline, addressqueue.aggregate, addressqueue.before_timestamp, addressqueue.limit, "usd", "base",  proxy.port)
                #  tokens_info = Get_Token_Dexscreen(self.sourcetype, self.chain_id, addresses, proxy.port)
                if tokens_info == "FAILED":
                    print(f"Request failed for addresses {addressqueue.pool_addresses}. Retrying...")
                    failure_count += 1
                    time.sleep(2)
                    if failure_count >= max_failures:
                        self.proxy_pool.remove_proxy(proxy)
                else:
                    with self.result_lock:
                        self.results.extend(tokens_info)
                    success = True  # 请求成功，设置 success 为 True
            except Exception as e:
                print(f"Exception occurred: {e}")
                failure_count += 1
                time.sleep(2)
                if failure_count >= max_failures:
                    self.proxy_pool.remove_proxy(proxy)
            finally:
                if proxy_acquired:
                    self.proxy_pool.release_proxy(proxy, semaphore)
                    proxy_acquired = False  # 重置标记

        if not success:
            print(f"Failed to process addresses {addressqueue.pool_addresses} after {max_failures} attempts.")

            self.failed_tasks.put(addressqueue)
        return success


    def monitor_failed_proxies(self):
        while not self.stop_event.is_set():
            with self.proxy_pool.lock:
                for port in self.proxy_pool.failed_proxies[:]:
                    ip = self.check_proxy(port)
                    if ip:
                        self.proxy_pool.proxies[port].is_available = True
                        self.proxy_pool.proxies[port].ip = ip
                        # 重新创建限速器和信号量
                        storage = MemoryStorage()
                        limiter = Limiter(self.proxy_pool.rate, self.proxy_pool.capacity, storage)
                        semaphore = threading.Semaphore(self.proxy_pool.max_threads_per_proxy)
                        self.proxy_pool.proxy_info[port] = {
                            'limiter': limiter,
                            'semaphore': semaphore
                        }
                        self.proxy_pool.failed_proxies.remove(port)
                        print(f"Proxy {port} restored and added back to pool.")
            if self.stop_event.wait(timeout=60):
                break  # 如果 stop_event 被设置，跳出循环

    def check_proxy(self, port: int) -> bool:
        # 实现您的代理检查逻辑，例如尝试建立连接等
        proxy = "127.0.0.1:" + str(port)
        ip = testproxy.fetch_public_ip_via_http_proxy(proxy)
        if not ip:
            print(f"Failed to fetch public IP via proxy {proxy}.")
            return False
        return ip  # 返回代理的 IP 表示代理可用