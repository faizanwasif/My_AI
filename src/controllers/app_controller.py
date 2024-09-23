import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, pyqtSignal
from src.models.app_model import AppModel
from src.views.app_view import AppView
import config

class WorkerThread(QThread):
    result_ready = pyqtSignal(str)

    def __init__(self, model, user_input):
        super().__init__()
        self.model = model
        self.user_input = user_input

    def run(self):
        result = self.model.process_input(self.user_input)
        self.result_ready.emit(result)

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.model = AppModel()
        self.view = AppView()

        self.view.set_submit_command(self.submit)
        self.view.set_quit_command(self.quit)
        # self.view.update_article_count.connect(self.update_article_count)  # Connect new signal

    def run(self):
        self.view.show()
        sys.exit(self.app.exec())

    def submit(self):
        user_input = self.view.get_input()
        self.view.clear_input()
        
        self.worker = WorkerThread(self.model, user_input)
        self.worker.result_ready.connect(self.view.display_results)
        self.worker.start()

    def quit(self):
        self.model.stop()
        self.app.quit()

    def update_article_count(self, count):
        config.article_count = count
        print(f"Article count updated to: {config.article_count}")  # For debugging

if __name__ == "__main__":
    controller = AppController()
    controller.run()