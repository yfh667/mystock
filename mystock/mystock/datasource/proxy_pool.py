"""代理池 —— 复用原 crypto 项目 proxymultithread / testproxy 的思路。

东方财富按 IP 限速，单 IP 密集请求会被掐断(RemoteDisconnected)。
clash 已把每个节点映射到一个本地端口(50000+)，每个端口是一个不同出口 IP。
本模块负责：
    1) 探活(probe)：并发测试哪些端口当前可用
    2) 轮换(get)：线程安全地轮流分发可用端口，供并发请求绕开单 IP 限流

不限流时也可不用代理池（直连最快）；限流或要并发提速时启用。
"""
from __future__ import annotations

import itertools
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional

import requests

# 探活用的轻量东财请求（只取很少数据，快速判断端口是否通）
_PROBE_URL = "https://82.push2.eastmoney.com/api/qt/clist/get"
_PROBE_PARAMS = {
    "pn": 1, "pz": 5, "po": 1, "np": 1, "fltt": 2,
    "fs": "m:1 t:2", "fields": "f12,f14",
}

# 翻墙探活：判断节点能否访问国外（用于 Yahoo 等海外源）。
# clash 节点出口在国外，访问东财(国内)成功率低，但访问 google/yahoo 成功率高，
# 所以海外源应该用 target='google' 探活。
_GOOGLE_PROBE = "https://www.google.com/generate_204"


def _proxies_for(port: int) -> dict:
    url = f"http://127.0.0.1:{port}"
    return {"http": url, "https": url}


class ProxyPool:
    """clash 多端口代理池。"""

    def __init__(
        self,
        start_port: int = 50000,
        end_port: int = 50058,
        *,
        include_direct: bool = False,
    ):
        """:param include_direct: 是否把"本机直连"也作为一个出口纳入轮换。"""
        self.candidate_ports = list(range(start_port, end_port))
        self.include_direct = include_direct
        self.available: List[Optional[int]] = []   # None 代表直连
        self._cycle = None
        self._lock = threading.Lock()

    # ---------- 探活 ----------
    @staticmethod
    def _probe_one(port: int, timeout: float, target: str = "eastmoney") -> bool:
        """target='eastmoney' 测国内东财；target='google' 测翻墙能力(海外源用)。"""
        try:
            px = _proxies_for(port)
            if target == "google":
                return requests.get(_GOOGLE_PROBE, proxies=px, timeout=timeout).status_code == 204
            r = requests.get(_PROBE_URL, params=_PROBE_PARAMS, timeout=timeout, proxies=px)
            return bool(r.json().get("data", {}).get("diff"))
        except Exception:  # noqa: BLE001
            return False

    def probe(
        self, *, target: str = "eastmoney", timeout: float = 8.0,
        max_workers: int = 30, verbose: bool = False,
    ) -> List[Optional[int]]:
        """并发探活，刷新可用端口列表，返回之。

        :param target: 'eastmoney'(国内直连源) 或 'google'(海外源如 Yahoo)。
        """
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            flags = list(ex.map(lambda p: self._probe_one(p, timeout, target), self.candidate_ports))
        ports: List[Optional[int]] = [p for p, ok in zip(self.candidate_ports, flags) if ok]
        if self.include_direct:
            ports.append(None)
        with self._lock:
            self.available = ports
            self._cycle = itertools.cycle(ports) if ports else None
        if verbose:
            print(f"[ProxyPool] 可用出口 {len(ports)}/{len(self.candidate_ports)}: {ports}")
        return ports

    # ---------- 轮换 ----------
    def get(self) -> Optional[dict]:
        """线程安全地取下一个出口的 proxies dict；None 表示直连/无可用。"""
        with self._lock:
            if not self._cycle:
                return None
            port = next(self._cycle)
        return None if port is None else _proxies_for(port)

    def __len__(self) -> int:
        return len(self.available)
