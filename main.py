import time
from scraper.electricity_scraper import ElectricityScraper
from config.config import ConfigManager
from notifier import NotifierFactory


class Main:
    def __init__(self):
        self.config = ConfigManager("config.ini")
        self.scraper = ElectricityScraper(self.config)

        # 创建 Notifier 实例列表
        platforms = self.config.get("Notification", "platform").split(',')
        self.notifiers = [NotifierFactory.create_notifier(platform, self.config) for platform in platforms]

    def notify(self, amount):
        message = f"当前电费：{amount}元"
        for notifier in self.notifiers:
            notifier.send(amount, message)

    def run(self, retry_times=3, retry_interval=60):
        for i in range(retry_times):
            try:
                amount = self.scraper.fetch_data()
                self.notify(amount)
                return amount
            except Exception as err:
                if i < retry_times - 1:
                    print(f'尝试 {i + 1}次 失败，错误：{err}。 等待 {retry_interval}秒后再次尝试。')
                    time.sleep(retry_interval)
                else:
                    print(f'尝试 {i + 1}次 失败，错误: {err}。 无更多尝试。')


if __name__ == "__main__":
    main_instance = Main()
    retry_times = int(main_instance.config.get("Retry", "retry_times"))
    retry_interval = int(main_instance.config.get("Retry", "retry_interval"))
    print(main_instance.run(retry_times=retry_times, retry_interval=retry_interval))
