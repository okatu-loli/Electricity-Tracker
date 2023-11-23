import random
import time
import scraper.slider_image_process as sip

from playwright.sync_api import sync_playwright

class ElectricityScraper:
    def __init__(self, config):
        print("初始化 ElectricityScraper")
        print("初始化 self.config")
        self.config = config
        print("self.config 初始化完成")
        print("ElectricityScraper 初始化完成")

    def fetch_data(self):
        with sync_playwright() as pw:
            print("尝试启动浏览器")
            self.browser = pw.chromium.launch(
                # executable_path='C:\\Users\\ZeLin\\AppData\\Local\\ms-playwright\\chromium-1084\\chrome-win\\chrome.exe',
                headless=True)
            print("浏览器启动完成")
            self.context = self.browser.new_context(viewport={'width': 1920, 'height': 1080})
            self.page = self.context.new_page()

            self.page.goto("https://www.95598.cn/osgweb/login")
            self.page.locator(".user").click()
            self.page.get_by_placeholder("请输入用户名/手机号/邮箱").fill(self.config.get('Credentials', 'username'))
            self.page.get_by_placeholder("请输入密码").fill(self.config.get('Credentials', 'password'))

            self.page.get_by_role("button", name="登录").click()

            # 抓取验证码数据
            self.loading_slide()
            self.page.wait_for_selector('canvas')
            slide_bg_img = self.page.evaluate("() => document.querySelector('canvas').toDataURL('image/png')")
            slide_block_img = self.page.evaluate(
                "() => document.querySelector('.slide-verify-block').toDataURL('image/png')")

            # with open('slide_bg_img.png', 'wb') as f:
            #     f.write(base64.b64decode(str(slide_bg_img).split(',')[-1], altchars=None, validate=False))
            # with open('slide_block_img.png', 'wb') as f:
            #     f.write(base64.b64decode(str(slide_block_img).split(',')[-1], altchars=None, validate=False))

            slide_bg_img = sip.base64_to_img(slide_bg_img)
            slide_block_img = sip.cutting_transparent_block(sip.base64_to_img(slide_block_img), offset=65)
            Loc = sip.identify_gap(slide_bg_img, slide_block_img)

            # 计算矫正滑块移动距离
            distance = 0.0
            special_block = sip.check_special_block(slide_block_img)
            if special_block:
                distance = Loc[0] - 4
            else:
                distance = Loc[0] - 13
            distance = distance / 350.946 * 371
            # print('special_block=',special_block)
            # print('distance=', distance)

            self.move_slide(distance)

            try:
                while self.page.locator(".cff8").nth(0).get_by_text('元').inner_text(timeout=5000)[:-1] == "--":
                    time.sleep(0.5)
                amount = float(self.page.locator(".cff8").nth(0).get_by_text('元').inner_text()[:-1])
                print(f"今日电费：{amount}")
            except:
                self.page.screenshot(path='debug.png', full_page=True)

                self.page.close()
                self.context.close()
                self.browser.close()
                raise TimeoutError("Authentication or network error")

            self.page.close()
            self.context.close()
            self.browser.close()

            return amount

    # Todo:不通过硬盘检测
    def loading_slide(self, timeout = 10):
        """等待验证码图片加载"""
        while True:
            self.page.locator("canvas").nth(0).screenshot(path='slide.png')
            if not sip.is_monochrome('slide.png'):
                break
            time.sleep(0.5)
            print("Waiting slide image ...")

            timeout -= 1
            if timeout <= 0:
                self.page.close()
                self.context.close()
                self.browser.close()
                raise TimeoutError("Timeout in wait slide image")

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
        self.page.mouse.up()


if __name__ == "__main__":
    config = {}
    electricityScraper = ElectricityScraper(config)
    electricityScraper.fetch_data()
