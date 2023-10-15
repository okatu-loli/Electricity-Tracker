import requests
from .base_notifier import BaseNotifier


class ServerChanNotifier(BaseNotifier):

    def send(self, amt, message):
        url = f"https://sctapi.ftqq.com/{self.config.get('ServerChan', 'send_key')}.send"
        params = {
            'text': '电费提醒',
            'desp': message
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            print("通知已发送")
        else:
            print("发送通知失败")
