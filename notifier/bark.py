import json

import requests

from .base_notifier import BaseNotifier


class BarkNotifier(BaseNotifier):

    def send(self, amt, message):
        url = f"{self.config.get('Bark','url')}/{self.config.get('Bark','token')}/{message}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            'amount': amt,
            'message': message
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            print("通知已发送")
        else:
            print("发送通知失败")
