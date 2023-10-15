import configparser
import os

class ConfigManager:
    def __init__(self, config_path):
        self.config = configparser.ConfigParser()
        self.config.read(config_path, encoding='utf-8')

    def get(self, section, key):
        if key == 'username':
            username = os.getenv('ELECTRICITY_USER')
            if username != None:
                return username
        if key == 'password':
            password = os.getenv('ELECTRICITY_PASS')
            if password != None:
                return password

        return self.config.get(section, key)
