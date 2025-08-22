from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os


class MEXCAutoDownloader:
    def __init__(self, headless=False, proxy=None):
        self.options = webdriver.ChromeOptions()
        if headless:
            self.options.add_argument("--headless=new_cex_monitor")
        if proxy:
            self.options.add_argument(f"--proxy-server={proxy}")

        # 伪装浏览器指纹
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)

        self.driver = webdriver.Chrome(options=self.options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def login(self, username, password):
        """处理可能的登录流程"""
        self.driver.get("https://www.mexc.com/login")
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#email"))
            ).send_keys(username)

            self.driver.find_element(By.CSS_SELECTOR, "#password").send_keys(password)
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            # 处理二次验证
            WebDriverWait(self.driver, 20).until(
                lambda d: "dashboard" in d.current_url
            )
        except Exception as e:
            print("登录异常:", str(e))

    def download_data(self, symbol=None):
        """核心下载逻辑"""
        self.driver.get("https://www.mexc.com/zh-MY/market-data-download")

        # 智能等待页面加载
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".mc_market_list_table"))
        )

        # 动态搜索交易对
        if symbol:
            search_box = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder='搜索币种']")
            search_box.clear()
            for char in symbol:
                search_box.send_keys(char)
                time.sleep(0.2)  # 模拟人工输入

            time.sleep(1)

        # 识别下载按钮并点击
        buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(),'下载')]")
        for btn in buttons:
            try:
                btn.click()
                time.sleep(3)  # 等待下载弹窗

                # 处理浏览器原生下载
                latest_file = self.monitor_downloads()
                if latest_file:
                    print(f"文件已下载: {latest_file}")
            except Exception as e:
                print("下载异常:", str(e))

    def monitor_downloads(self, timeout=30):
        """监控下载目录获取最新文件"""
        download_dir = os.path.expanduser("~/Downloads")
        initial_files = set(os.listdir(download_dir))

        end_time = time.time() + timeout
        while time.time() < end_time:
            current_files = set(os.listdir(download_dir))
            new_files = current_files - initial_files
            if new_files:
                return max(
                    (os.path.join(download_dir, f) for f in new_files),
                    key=lambda x: os.path.getmtime(x)
                )
            time.sleep(1)
        return None

    def __del__(self):
        try:
            self.driver.quit()
        except:
            pass


# 使用示例
if __name__ == "__main__":
    bot = MEXCAutoDownloader(
        headless=False,  # 调试时设为可见
        proxy="socks5://127.0.0.1:7890"  # 可选代理
    )

    # 如果需要登录
    # bot.login("your_email", "your_password")

    bot.download_data("BTC_USDT")
