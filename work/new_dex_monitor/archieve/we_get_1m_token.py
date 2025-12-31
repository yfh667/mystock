

import dexprice.modules.allmodules.project as project
from dexprice.modules.utilis.define import FilterCriteria
from dexprice.modules.utilis.define import FilterCriteria
import dexprice.modules.db.insert_db as insert_db
import os
import dexprice.modules.utilis.findroot as findroot
import dexprice.modules.allmodules.realtoken as realtoken

import dexprice.modules.PriceMonitor.tokenflitter as tokenflitter

import dexprice.modules.proxy.proxymultitheread as proxymultitheread

import dexprice.modules.PriceMonitor.dexscreen_parrel as dexscreen_parrel

import dexprice.modules.utilis.define as define

from datetime import datetime
from pathlib import Path
from typing import Iterable, Any, List

def _get_val(obj: Any, key: str):
    """兼容对象属性 和 dict 键"""
    if obj is None:
        return None
    if hasattr(obj, key):
        return getattr(obj, key)
    if isinstance(obj, dict):
        return obj.get(key)
    return None


def export_addresses2(addresses: List[str], outdir: str = ".") -> str:
    """
    将输入的地址列表：
      1) 打印到控制台
      2) 保存到 `M-D-H-m.txt`（示例：9-14-20-13.txt）

    参数:
      addresses: 一个包含地址字符串的列表，例如 ['0x123...', '0xabc...']
      outdir: 输出文件夹路径

    返回:
      写入文件的绝对路径
    """

    # 1. 去重并保持顺序
    seen = set()
    valid_addrs: List[str] = []

    for addr in addresses:
        # 过滤掉 None 或 空字符串，并去重
        if addr and isinstance(addr, str) and (addr not in seen):
            seen.add(addr)
            valid_addrs.append(addr)

    # 2. 控制台输出
    if valid_addrs:
        print(f"[INFO] {len(valid_addrs)} unique addresses found:")
        for a in valid_addrs:
            print(a)
    else:
        print("[INFO] No valid addresses to export.")
        # 如果没有数据，直接返回空字符串或根据需求处理
        return ""

    # 3. 生成文件名与目录 (注意这里使用了 datetime.datetime.now())
    now = datetime.now()
    filename = f"{now.month}-{now.day}-{now.hour}-{now.minute}.txt"

    out_path = Path(outdir)
    out_path.mkdir(parents=True, exist_ok=True)
    file_path = out_path / filename

    # 4. 写文件
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            for a in valid_addrs:
                f.write(a + "\n")

        abs_path = str(file_path.resolve())
        print(f"[INFO] Saved to: {abs_path}")
        return abs_path

    except Exception as e:
        print(f"[ERROR] Failed to write file: {e}")
        return ""
def compute_token_new_add(token_new: Iterable[Any],
                          token_raw: Iterable[Any],
                          key: str = "address") -> List[Any]:
    """
    计算差集：返回 token_new 中按 key 不在 token_raw 的 token 列表。
    按 address 去重且保持原顺序。
    """
    raw_set = set()
    for t in token_raw:
        v = _get_val(t, key)
        if v:
            raw_set.add(v)

    seen = set()
    token_new_add: List[Any] = []
    for t in token_new:
        v = _get_val(t, key)
        if v and (v not in raw_set) and (v not in seen):
            seen.add(v)
            token_new_add.append(t)

    return token_new_add

def export_addresses(tokens: Iterable[Any],
                     key: str = "address",
                     outdir: str = ".") -> str:
    """
    将 tokens 的 address：
      1) 打印到控制台
      2) 保存到 `M-D-H-m.txt`（示例：9-14-20-13.txt）
    返回写入文件的绝对路径。
    """
    # 提取地址，去重保序
    seen = set()
    addrs: List[str] = []
    for t in tokens:
        v = _get_val(t, key)
        if v and v not in seen:
            seen.add(v)
            addrs.append(v)

    # 控制台输出
    if addrs:
        print(f"[INFO] {len(addrs)} new addresses:")
        for a in addrs:
            print(a)
    else:
        print("[INFO] No addresses to export.")

    # 生成文件名与目录
    now = datetime.now()
    filename = f"{now.month}-{now.day}-{now.hour}-{now.minute}.txt"  # 例：9-14-20-13.txt
    out_path = Path(outdir)
    out_path.mkdir(parents=True, exist_ok=True)
    file_path = out_path / filename

    # 写文件
    with open(file_path, "w", encoding="utf-8") as f:
        for a in addrs:
            f.write(a + "\n")

    print(f"[INFO] Saved to: {file_path.resolve()}")
    return str(file_path.resolve())

# ================= 用 法 =================
# 先算差集 -> token_new_add



def extract_valid_tokens(token_new,criteria):
    # 初始化字典，用链名作为键，地址列表作为值
    chain_addresses = {
        'solana': []

    }

    # 遍历 token_new，根据链名将地址加入对应的列表
    for token in token_new:
        # 确保 token.chainid 是链名，并存在于字典的键中
        if token.chainid in chain_addresses:
            chain_addresses[token.chainid].append(token.pair_address)  # 添加地址到对应链的列表
    # all the token that satisfied the request
    tokenreal = []
    # # 示例：打印每个链名及其对应的地址列表

    sourcetype = define.Config.DEXS
    max_threads_per_proxy = 2
    clash_api_url = "http://127.0.0.1:9097"
    headers = {"Authorization": "Bearer manba"}
    rate = 5
    capacity = 300
    startport = 50000
    for chain, pairaddresses in chain_addresses.items():
        print(f"we check Chain: {chain} ")
        chainid = chain

        proxys = proxymultitheread.get_one_ip_proxy_multithread(startport, clash_api_url, headers)
        task_manager = dexscreen_parrel.TaskManager(pairaddresses, sourcetype, chainid, proxys, rate, capacity,
                                                    max_threads_per_proxy, 'get  ' + chainid)
        tokensinfo, failed_tasks = task_manager.run()
        for token in tokensinfo:

            if (tokenflitter.normal_token_filter(token, criteria)):
                if (token.creattime == '1970-01-01 00:00:00'):
                    pass
                else:
                    tokenreal.append(token)

    return tokenreal



if __name__ == "__main__":
    criteria = FilterCriteria(
        liquidity_usd_min=100000,
        liquidity_usd_max=None,
        fdv_min=1000000,
        fdv_max=None,
        pair_age_min_hours=None,
        pair_age_max_hours= None
    )



    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = findroot.find_project_root(current_dir)


    DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")

    db_folder = DATA_FOLDER+'/dex'  # 数据库存储文件夹
    #   我们读取这个原始的数据库文件，这个一半是全部valid的
    db_name = 'all.db'  # 数据库文件名

    db = insert_db.SQLiteDatabase(db_folder, db_name)
    db.connect()
    token_new = db.readdbtoken()


# here 我们进行筛选
    tokenreal = extract_valid_tokens(token_new ,criteria)

#
    db.close()

    db_folder2 = db_folder +'/one_mtoken'
    db_name2 = 'one_mtoken.db'  # 数据库文件名
    db = insert_db.SQLiteDatabase(db_folder2, db_name2)
    db.connect()

    token_raw = db.readdbtoken()
    #  接下来，我们要做的是，如果tokenreal出现了token_raw没有得token，需要打印出来，同时，发送到

    token_new_add = compute_token_new_add(tokenreal, token_raw)



    db.insert_multiple_tokeninfo2(token_new_add)

    export_addresses(token_new_add, outdir=".")
    #db.insert_multiple_tokeninfo(tokenreal)



    db.close()


