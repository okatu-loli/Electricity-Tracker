import paho.mqtt.client as mqtt
from .base_notifier import BaseNotifier


class MQTTNotifier(BaseNotifier):

    def send(self, amt, message):
        client = mqtt.Client()
        client.connect(self.config.get('MQTT', 'mqtt_host'),
                       int(self.config.get('MQTT', 'mqtt_port')), 60)
        client.publish(self.config.get('MQTT', 'mqtt_topic'), message)
        client.disconnect()
