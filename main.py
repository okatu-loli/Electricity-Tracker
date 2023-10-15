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
        if len(platforms) == 1 and platforms[0] == '':
            self.notifiers = []
        else:
            self.notifiers = [NotifierFactory.create_notifier(platform, self.config) for platform in platforms]

    def notify(self, amount):
        message = f"当前电费：{amount}元"
        for notifier in self.notifiers:
            notifier.send(amount,message)

    def run(self):
        amount = self.scraper.fetch_data()
        self.notify(amount)


if __name__ == "__main__":
    main_instance = Main()

    enable_timing = main_instance.config.get("Notification", "enable_timing")
    if enable_timing.lower() == "true":
        notification_time = main_instance.config.get("Notification", "time")
        hour, minute, second = map(int, notification_time.split(":"))

        scheduler = BlockingScheduler()
        scheduler.add_job(main_instance.run, 'interval', hours=24, start_date=f'2023-10-14 {hour}:{minute}:{second}')
        scheduler.start()
    else:
        main_instance.run()
