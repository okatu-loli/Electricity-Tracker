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

logging.basicConfig(filename=LOG_FILE_PATH, level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class Main:
    def __init__(self):
        self.config = ConfigManager("config.ini")
        self.scraper = ElectricityScraper(self.config)
        self.notifiers = None

        # 创建 Notifier 实例列表
        platforms = self.config.get("Notification", "platform").split(',')
        if not platforms == ['']:
            self.notifiers = [NotifierFactory.create_notifier(platform, self.config) for platform in platforms]

    def notify(self, amount):
        message = f"当前电费：{amount}元"
        for notifier in self.notifiers:
            notifier.send(amount, message)

    def run(self, retry_times=3, retry_interval=60):
        for i in range(retry_times):
            try:
                amount = self.scraper.fetch_data()
                if self.notifiers:
                    self.notify(amount)
                return amount
            except TimeoutError as err:
                if i < retry_times - 1:
                    logging.error(f'尝试 {i + 1}次 失败，错误：{err}。 等待 {retry_interval}秒后再次尝试。')
                    time.sleep(retry_interval)
                else:
                    logging.error(f'尝试 {i + 1}次 失败，错误: {err}。 无更多尝试。')


if __name__ == "__main__":
    main_instance = Main()
    retry_times = int(main_instance.config.get("Retry", "retry_times"))
    retry_interval = int(main_instance.config.get("Retry", "retry_interval"))
    print(main_instance.run(retry_times=retry_times, retry_interval=retry_interval))
