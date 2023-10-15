import requests
import json
from .base_notifier import BaseNotifier


class WebhookNotifier(BaseNotifier):
    """
    可以用 Webhook 直接发送到 Home Assistant
    Home Assisistant 中的 sensor 参考配置如下
    - trigger:
        - platform: webhook
          webhook_id: {your_webhook_id}
          local_only: false
          allowed_methods:
            - POST
      sensor:
        - name: "Current Electricity Bill"
          unique_id: Tei9S161spDNZDP7
          state: "{{ trigger.json.amount }}"
        - name: "Current Electricity Message"
          unique_id: k0q0GTHrWcczneHw
          state: "{{ trigger.json.msg }}"
    """
    def send(self, amt, message):
        url = self.config.get('Webhook', 'webhook_url')
        headers = {'Content-Type': 'application/json'}
        payload = {
            'amount': amt,
            'message': message
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            print('通知已发送')
        else:
            print('发送通知失败')
