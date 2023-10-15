import requests
import json
from .base_notifier import BaseNotifier


class FeishuNotifier(BaseNotifier):

    def send(self, amt, message):
        url = f"https://open.feishu.cn/open-apis/bot/v2/hook/{self.config.get('Feishu', 'robot_token')}"
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
