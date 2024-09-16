import threading
from src.models.app_model import AppModel
from src.views.app_view import AppView

class AppController:
    def __init__(self):
        self.model = AppModel()
        self.view = AppView()

        self.view.set_submit_command(self.submit)
        self.view.set_quit_command(self.quit)

    def run(self):
        self.view.mainloop()

    def submit(self):
        user_input = self.view.get_input()
        self.view.clear_input()
        
        def process_and_display():
            result = self.model.process_input(user_input)
            self.view.display_results(result)

        threading.Thread(target=process_and_display, daemon=True).start()

    def quit(self):
        self.model.stop()
        self.view.quit()