from .base_notifier import BaseNotifier


class LocalFileNotifier(BaseNotifier):

    def send(self, amt, message):
        filepath = self.config.get('LocalFile', 'file_path')
        with open(filepath, 'w') as file:
            file.write(message)