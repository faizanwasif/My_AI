import sys
import asyncio
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, pyqtSignal, QObject, QRunnable, QThreadPool
from src.models.app_model import AppModel
from src.views.app_view import AppView
import config

class WorkerSignals(QObject):
    result_ready = pyqtSignal(str)
    error = pyqtSignal(str)

class AsyncWorker(QRunnable):
    def __init__(self, model, user_input):
        super().__init__()
        self.model = model
        self.user_input = user_input
        self.signals = WorkerSignals()

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.model.process_input(self.user_input))
            self.signals.result_ready.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            loop.close()

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.model = AppModel()
        self.view = AppView()
        self.threadpool = QThreadPool()

        self.view.set_submit_command(self.submit)
        self.view.set_quit_command(self.quit)

    def run(self):
        self.view.show()
        sys.exit(self.app.exec())

    def submit(self):
        user_input = self.view.get_input()
        self.view.clear_input()
        
        worker = AsyncWorker(self.model, user_input)
        worker.signals.result_ready.connect(self.view.display_results)
        worker.signals.error.connect(self.handle_error)
        self.threadpool.start(worker)

    def quit(self):
        self.model.stop()
        self.app.quit()

    def update_article_count(self, count):
        config.article_count = count
        print(f"Article count updated to: {config.article_count}")  # For debugging

    def handle_error(self, error_message):
        print(f"Error occurred: {error_message}")
        # You can also update the view to display the error message if needed
        # self.view.display_error(error_message)

if __name__ == "__main__":
    controller = AppController()
    controller.run()