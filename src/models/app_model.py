from .web_crawler_model import WebCrawlerModel

class AppModel:
    def __init__(self):
        self._data = ""
        self._running = True
        self.web_crawler = WebCrawlerModel()

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def running(self):
        return self._running

    def stop(self):
        self._running = False

    def process_input(self, user_input):
        return self.web_crawler.process_input(user_input)