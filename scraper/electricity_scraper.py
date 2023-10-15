import time

import ddddocr
from playwright.sync_api import sync_playwright


class ElectricityScraper:
    def __init__(self, config):
        print("初始化 ElectricityScraper")
        print("初始化 self.config")
        self.config = config
        print("self.config 初始化完成")
        print("初始化 ddddocr")
        self.ocr = ddddocr.DdddOcr()
        print("ddddocr 初始化完成")
        print("ElectricityScraper 初始化完成")

    def fetch_data(self):
        with sync_playwright() as pw:
            print("尝试启动浏览器")
            browser = pw.firefox.launch(headless=True)
            print("浏览器启动完成")
            context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = context.new_page()

            page.goto("https://www.95598.cn/osgweb/login")
            page.locator(".user").click()
            page.get_by_placeholder("请输入用户名/手机号/邮箱").fill(self.config.get('Credentials', 'username'))
            page.get_by_placeholder("请输入密码").fill(self.config.get('Credentials', 'password'))
            page.locator(".code-mask").screenshot(path="yzm.png")

            with open("yzm.png", 'rb') as f:
                img_bytes = f.read()
            res = self.ocr.classification(img_bytes)
            print("图形验证码:", res)

            page.get_by_role("textbox", name="请输入验证码").fill(res)
            page.get_by_role("button", name="登录").click()

            while page.locator(".cff8").get_by_text('元').inner_text(timeout=5000)[:-1] == "--":
                time.sleep(1)
            amount = float(page.locator(".cff8").get_by_text('元').inner_text()[:-1])
            print(f"今日电费：{amount}")

            page.close()
            context.close()
            browser.close()

            return amount
