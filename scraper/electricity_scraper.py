import base64
import io
import logging
import os
import random
import time

import scraper.slider_image_process as sip

from playwright.sync_api import sync_playwright

ROOT_DIRECTORY = os.path.dirname("./")
DEBUG_DIRECTORY = os.path.join(ROOT_DIRECTORY, 'debug')

# 检查并创建 debug 文件夹
if not os.path.exists(DEBUG_DIRECTORY):
    os.makedirs(DEBUG_DIRECTORY)

class ElectricityScraper:
    def __init__(self, config, ST_addition = 0, PT_addition = 0):
        logging.info("初始化 ElectricityScraper")
        self.slide_timeout = int(config.get('Retry', 'slide_timeout')) + ST_addition
        self.page_timeout = int(config.get('Retry', 'page_timeout')) + PT_addition
        self.debug = int(config.get('DEBUG', 'debug'))
        logging.info(f"slide_timeout = {self.slide_timeout}, page_timeout = {self.page_timeout}, debug = {self.debug}")

        self.username = config.get('Credentials', 'username')
        self.password = config.get('Credentials', 'password')
        logging.info("ElectricityScraper 初始化完成")

    def fetch_data(self):
        with sync_playwright() as pw:
            logging.info("尝试启动浏览器")
            self.browser = pw.chromium.launch(
                # executable_path='C:\\Users\\ZeLin\\AppData\\Local\\ms-playwright\\chromium-1084\\chrome-win\\chrome.exe',
                headless=True)
            logging.info("浏览器启动完成")
            self.context = self.browser.new_context(viewport={'width': 1920, 'height': 1080})
            self.page = self.context.new_page()

            self.page.goto("https://www.95598.cn/osgweb/login")
            self.page.locator(".user").click()
            self.page.get_by_placeholder("请输入用户名/手机号/邮箱").fill(self.username)
            self.page.get_by_placeholder("请输入密码").fill(self.password)

            self.page.get_by_role("button", name="登录").click()
            self.debug_save_img("login")
            logging.info("登录页面加载完成")

            # 抓取验证码数据
            self.loading_slide(self.slide_timeout * 2)
            self.page.wait_for_selector('canvas')
            self.slide_bg_img = self.page.evaluate("() => document.querySelector('canvas').toDataURL('image/png')")
            self.slide_block_img = self.page.evaluate(
                "() => document.querySelector('.slide-verify-block').toDataURL('image/png')")
            self.debug_save_img(slide=True)
            logging.info("验证码数据加载完成")

            distance = self.calc_distance()
            logging.info("滑块距离计算完成")

            self.move_slide(distance)
            logging.info("滑块移动完成")

            self.loading_page(self.page_timeout * 2)
            logging.info("页面加载完成")


            while self.page.locator(".cff8").nth(0).get_by_text('元').inner_text()[:-1] == "--":
                logging.info(f"正在尝试获取值...")
                time.sleep(0.5)
            amount = float(self.page.locator(".cff8").nth(0).get_by_text('元').inner_text()[:-1])
            logging.info(f"获取到值：{amount}")

            self.debug_save_img("page")
            self.close()
            return amount

    def loading_slide(self, timeout, intervals = 0.5):
        """等待验证码图片加载"""
        while True:
            slide = self.page.locator("canvas").nth(0).screenshot()
            memory_file = io.BytesIO(slide)
            if not sip.is_monochrome(memory_file):
                break
            time.sleep(intervals)
            logging.info("等待验证码图片加载...")

            timeout -= 1
            if timeout <= 0:
                self.close()
                raise TimeoutError("验证码加载超时")

    def loading_page(self, timeout, intervals = 500):
        """等待页面加载"""
        while True:
            try:
                self.page.locator(".cff8").nth(0).get_by_text('元').inner_text(timeout=intervals / 2)
            except:
                pass
            else:
                break

            try:
                self.page.locator("span").get_by_text('验证错误').inner_text(timeout=intervals / 2)
            except:
                pass
            else:
                self.debug_save_img("page")
                self.close()
                raise TimeoutError("验证错误")

            logging.info("等待页面加载...")

            timeout -= 1
            if timeout <= 0:
                self.debug_save_img("page")
                self.close()
                raise TimeoutError("页面加载超时")

    def move_slide(self, distance):
        """移动滑块"""
        slider_btn_rect = self.page.locator('#slideVerify div').nth(3).bounding_box()
        self.page.mouse.move(slider_btn_rect['x'] + 20, slider_btn_rect['y'] + 20)
        time.sleep(0.5)
        self.page.mouse.down()

        tracks = sip.get_tracks(distance)

        for x in tracks:
            self.page.mouse.move(slider_btn_rect['x'] + 20 + x, random.randint(-5, 5) + slider_btn_rect['y'] + 20)
        self.page.mouse.move(slider_btn_rect['x'] - 5 + tracks[-1] + 20,
                             random.randint(-5, 5) + slider_btn_rect['y'] + 20)
        self.page.mouse.move(slider_btn_rect['x'] + 5 + tracks[-1] + 20,
                             random.randint(-5, 5) + slider_btn_rect['y'] + 20)
        time.sleep(0.5)
        self.debug_save_img("move")
        self.page.mouse.up()

    def calc_distance(self):
        slide_bg_img = sip.base64_to_img(self.slide_bg_img)
        slide_block_img = sip.cutting_transparent_block(sip.base64_to_img(self.slide_block_img), offset=65)
        Loc = sip.identify_gap(slide_bg_img, slide_block_img)

        # 计算矫正滑块移动距离
        distance = 0.0
        special_block = sip.check_special_block(slide_block_img)
        if special_block:
            distance = Loc[0] - 4
        else:
            distance = Loc[0] - 13
        distance = distance / 350.946 * 371
        if self.debug:
            with open(f'{DEBUG_DIRECTORY}/{time.strftime("%d-%b-%Y-%H-%M-%S", time.localtime())} distance.txt', 'w') as f:
                f.write(f"Loc[0]:{Loc[0]}px\ndistance:{distance}px")

        return distance

    def close(self):
        self.page.close()
        self.context.close()
        self.browser.close()

    def debug_save_img(self, filename = '', slide : bool = False):
        if self.debug:
            if slide:
                with open(f'{DEBUG_DIRECTORY}/{time.strftime("%d-%b-%Y-%H-%M-%S", time.localtime())} slide_bg_img.png',
                          'wb') as f:
                    f.write(base64.b64decode(str(self.slide_bg_img).split(',')[-1], altchars=None, validate=False))
                with open(f'{DEBUG_DIRECTORY}/{time.strftime("%d-%b-%Y-%H-%M-%S", time.localtime())} slide_block_img.png',
                          'wb') as f:
                    f.write(base64.b64decode(str(self.slide_block_img).split(',')[-1], altchars=None, validate=False))
            else:
                self.page.screenshot(path=f'{DEBUG_DIRECTORY}/{time.strftime("%d-%b-%Y-%H-%M-%S", time.localtime())} {filename}.png',
                                     full_page=True)
