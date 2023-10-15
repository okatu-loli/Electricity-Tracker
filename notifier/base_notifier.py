from abc import ABC, abstractmethod

class BaseNotifier(ABC):

    def __init__(self, config):
        self.config = config

    @abstractmethod
    def send(self, amt, message):
        """发送通知的抽象方法，需要在子类中具体实现"""
        pass
