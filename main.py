import time

from apscheduler.schedulers.blocking import BlockingScheduler

from config.config import ConfigManager
from notifier import NotifierFactory
from scraper.electricity_scraper import ElectricityScraper


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
                break
            except Exception as err:
                if i < retry_times - 1:
                    print(f'Try {i+1} failed, error: {err}. Wait for {retry_interval} seconds before next try.')
                    time.sleep(retry_interval)
                else:
                    print(f'Try {i+1} failed, error: {err}. No more tries.')


if __name__ == "__main__":
    main_instance = Main()

    enable_timing = main_instance.config.get("Notification", "enable_timing")
    if enable_timing.lower() == "true":
        notification_time = main_instance.config.get("Notification", "time")
        hour, minute, second = map(int, notification_time.split(":"))

        scheduler = BlockingScheduler()
        scheduler.add_job(main_instance.run(retry_times=int(main_instance.config.get("Retry", "retry_times")),
                                            retry_interval=int(main_instance.config.get("Retry", "retry_interval"))),
                          'interval', hours=24, start_date=f'2023-10-14 {hour}:{minute}:{second}')
        scheduler.start()
    else:
        main_instance.run(retry_times=int(main_instance.config.get("Retry", "retry_times")),
                          retry_interval=int(main_instance.config.get("Retry", "retry_interval")))
