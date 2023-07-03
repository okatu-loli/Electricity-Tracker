import time
import ddddocr
import requests
import json
import configparser
from playwright.sync_api import Playwright, sync_playwright

ocr = ddddocr.DdddOcr()


def run(pw: Playwright, nop: str, nom: int) -> None:
    browser = pw.firefox.launch(headless=True)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()

    page.goto("https://www.95598.cn/osgweb/login")
    page.locator(".user").click()
    page.get_by_placeholder("请输入用户名/手机号/邮箱").fill(username)
    page.get_by_placeholder("请输入密码").fill(password)
    page.locator(".code-mask").screenshot(path="yzm.png")

    with open("yzm.png", 'rb') as f:
        img_bytes = f.read()
    res = ocr.classification(img_bytes)
    print("图形验证码:", res)

    page.get_by_role("textbox", name="请输入验证码").fill(res)
    page.get_by_role("button", name="登录").click()

    while page.locator(".cff8").get_by_text('元').inner_text(timeout=5000)[:-1] == "--":
        time.sleep(1)
    amount = float(page.locator(".cff8").get_by_text('元').inner_text()[:-1])
    print(f"今日电费：{amount}")

    # 将电费保存到文件
    save_amount_to_file(amount)

    page.screenshot(path="example.png")

    enable_notify = config.get("Notification", "enable_notify")
    if enable_notify == 'true':
        if amount < nom:
            message = f"当前电费低于阈值：{amount}元"
            if nop == 'serverchan':
                send_notification_serverchan(message)
            elif nop == 'feishu':
                send_notification_feishu(message)

    enable_exec_notify = config.get("Notification", "enable_exec_notify")
    if enable_notify == 'true':
        if enable_exec_notify == 'true':
            if nop == 'serverchan':
                send_notification_serverchan(f"今日电费：{amount}")
            elif nop == 'feishu':
                send_notification_feishu(f"今日电费：{amount}")

    page.close()
    context.close()
    browser.close()


def send_notification_serverchan(message):
    url = f"https://sctapi.ftqq.com/{config.get('ServerChan', 'send_key')}.send"
    params = {
        'text': '电费提醒',
        'desp': message
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print("通知已发送")
    else:
        print("发送通知失败")


def send_notification_feishu(message):
    url = f"https://open.feishu.cn/open-apis/bot/v2/hook/{config.get('Feishu', 'robot_token')}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        'msg_type': 'text',
        'content': {
            'text': message
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        print("通知已发送")
    else:
        print("发送通知失败")


def file_copy(path_src, path_target):
    with open(path_src, 'rb') as rstream:
        content = rstream.read()
        with open(path_target, 'wb') as wstream:
            wstream.write(content)


def save_amount_to_file(amount):
    with open('electricity.txt', 'w') as file:
        file.write(f"今日电费:{amount}")


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')

    username = config.get('Credentials', 'username')
    password = config.get('Credentials', 'password')

    notification_platform = config.get('Notification', 'platform')
    notification_threshold = int(config.get('Notification', 'threshold'))

    with sync_playwright() as playwright:
        while True:
            try:
                run(playwright, notification_platform, notification_threshold)
                break
            except Exception as e:
                print(e)
