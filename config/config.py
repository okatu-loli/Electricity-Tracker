import configparser


class ConfigManager:
    def __init__(self, config_path):
        self.config = configparser.ConfigParser()
        self.config.read(config_path, encoding='utf-8')

    def get(self, section, key):
        return self.config.get(section, key)
