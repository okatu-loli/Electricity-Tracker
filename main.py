import logging
import os
import time
from datetime import date

from scraper.electricity_scraper import ElectricityScraper
from config.config import ConfigManager
from notifier import NotifierFactory

ROOT_DIRECTORY = os.path.dirname("./")
FILE_NAME = f'{date.today()}_log.txt'  # 将每天的日期加入到日志文件名中
LOG_DIRECTORY = os.path.join(ROOT_DIRECTORY, 'logs')

# 检查并创建 logs 文件夹
if not os.path.exists(LOG_DIRECTORY):
    os.makedirs(LOG_DIRECTORY)

LOG_FILE_PATH = os.path.join(LOG_DIRECTORY, FILE_NAME)

if not __name__ == "__main__":
    logging.basicConfig(filename=LOG_FILE_PATH, level=logging.INFO,format='%(asctime)s:%(levelname)s:%(message)s')

class Main:
    def __init__(self):
        self.config = ConfigManager("config.ini")
        self.retry_times = int(self.config.get("Retry", "retry_times"))
        self.retry_interval = int(self.config.get("Retry", "retry_interval"))
        self.page_timeout_addition = int(self.config.get("Retry", "page_timeout_addition"))
        self.slide_timeout_addition = int(self.config.get("Retry", "slide_timeout_addition"))
        self.notifiers = None

        # 创建 Notifier 实例列表
        platforms = self.config.get("Notification", "platform").split(',')
        if not platforms == ['']:
            self.notifiers = [NotifierFactory.create_notifier(platform, self.config) for platform in platforms]

    def notify(self, amount):
        message = f"当前电费：{amount}元"
        for notifier in self.notifiers:
            notifier.send(amount, message)

    def run(self):
        retry_pageErr = 0
        retry_slideErr = 0

        for i in range(self.retry_times):
            try:
                scraper = ElectricityScraper(self.config,
                                             ST_addition = retry_slideErr * self.slide_timeout_addition,
                                             PT_addition = retry_pageErr * self.page_timeout_addition)
                amount = scraper.fetch_data()
                if self.notifiers:
                    self.notify(amount)
                return amount
            except TimeoutError as err:
                if err.__str__() == "页面加载超时":
                    retry_pageErr += 1
                if err.__str__() == "验证码加载超时":
                    retry_slideErr += 1

                if i < self.retry_times - 1:
                    logging.error(f'尝试 {i + 1}次 失败，错误：{err}。 等待{self.retry_interval}秒后再次尝试。')
                    time.sleep(self.retry_interval)
                else:
                    logging.error(f'尝试 {i + 1}次 失败，错误: {err}。 无更多尝试。')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:%(message)s')

    main_instance = Main()
    print(main_instance.run())
