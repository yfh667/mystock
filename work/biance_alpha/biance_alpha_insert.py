# -*- coding: utf-8 -*-
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import os

from dexprice.modules.PriceMonitor import dexscreen_priceapi
from dexprice.modules.utilis.define import Config
import dexprice.modules.utilis.findroot as findroot
import dexprice.modules.db.insert_db as insert_db

APP_TITLE = "DexScreen Token 查询（GUI + 入库）"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("780x540")

        # ===== 顶部输入区 =====
        top = ttk.Frame(self, padding=12)
        top.pack(fill=tk.X, side=tk.TOP)

        ttk.Label(top, text="合约地址（CA）").grid(row=0, column=0, sticky="w")
        self.entry_ca = ttk.Entry(top)
        self.entry_ca.grid(row=1, column=0, sticky="we", pady=(4, 8))
        self.entry_ca.insert(0, "0x19Ed254efa5E061D28d84650891a3db2A9940C16")  # 可改可删
        self.entry_ca.bind("<Return>", lambda e: self.on_query_clicked())

        self.btn_query = ttk.Button(top, text="查询并入库", command=self.on_query_clicked)
        self.btn_query.grid(row=1, column=1, padx=(8, 0))

        self.btn_clear = ttk.Button(top, text="清空结果", command=self.clear_output)
        self.btn_clear.grid(row=1, column=2, padx=(8, 0))

        top.grid_columnconfigure(0, weight=1)

        # ===== 输出区 =====
        mid = ttk.Frame(self, padding=(12, 0, 12, 12))
        mid.pack(fill=tk.BOTH, expand=True)

        ttk.Label(mid, text="查询结果（多次查询会追加显示）").pack(anchor="w")
        self.txt_output = tk.Text(mid, height=24, wrap="none")
        self.txt_output.pack(fill=tk.BOTH, expand=True, pady=(4, 6))

        yscroll = ttk.Scrollbar(mid, command=self.txt_output.yview)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_output.configure(yscrollcommand=yscroll.set)

        # 状态栏
        self.status = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self, textvariable=self.status, anchor="w", padding=(10, 4))
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # ===== 计算数据库路径（与你脚本一致）=====
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = findroot.find_project_root(current_dir)
        data_folder = os.path.join(project_root, "Data")

        # 指定新的子目录
        self.db_folder = os.path.join(data_folder, "cex", "alpha")
        self.db_name = "biance_alpha.db"





    def set_busy(self, busy: bool):
        self.btn_query.configure(state=(tk.DISABLED if busy else tk.NORMAL))
        self.config(cursor=("watch" if busy else ""))
        self.status.set("查询中..." if busy else "就绪")

    def on_query_clicked(self):
        ca = self.entry_ca.get().strip()
        if not ca:
            messagebox.showwarning("提示", "请输入一个合约地址（CA）。")
            return

        self.append_output(f"\n=== 查询 ===\nCA: {ca}\n")
        self.set_busy(True)
        threading.Thread(target=self._query_and_insert_thread, args=(ca,), daemon=True).start()

    def _query_and_insert_thread(self, ca: str):
        try:
            # 固定：chain_id=''，proxy_port=None
            tokens_info = dexscreen_priceapi.Get_Token_Dexscreen(
                Config.DEXCA, '', [ca], 7890
            )

            # 1) 界面输出：保持原样打印 TokenInfo 列表的 __repr__
            self.append_output(str(tokens_info) + "\n")

            # 2) 入库：与你脚本一致的流程
            db = insert_db.SQLiteDatabase(self.db_folder, self.db_name)
            db.connect()
            try:
                # 你脚本里直接传了 tokens_info（通常是 [TokenInfo(...)] 列表）
                db.insert_multiple_tokeninfo(tokens_info)
                self.append_output("入库成功：Data/cex/alpha/biance_alpha.db\n")
            finally:
                db.close()

        except Exception as e:
            self.append_output(f"查询/入库失败：{repr(e)}\n")
        finally:
            self.set_busy(False)

    def append_output(self, text: str):
        self.after(0, lambda: (self.txt_output.insert(tk.END, text),
                               self.txt_output.see(tk.END)))

    def clear_output(self):
        self.txt_output.delete("1.0", tk.END)
        self.status.set("就绪")


if __name__ == "__main__":
    app = App()
    app.mainloop()
