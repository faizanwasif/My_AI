from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QSpinBox
from PyQt6.QtCore import Qt

class AppView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Web Crawler App")
        self.setGeometry(100, 100, 800, 600)
        self._create_widgets()

    def _create_widgets(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.label = QLabel("Enter your search query:")
        main_layout.addWidget(self.label)

        self.entry = QLineEdit()
        main_layout.addWidget(self.entry)

        article_count_layout = QHBoxLayout()
        self.article_count_label = QLabel("Number of articles:")
        self.article_count_input = QSpinBox()
        self.article_count_input.setMinimum(1)
        self.article_count_input.setMaximum(100)
        self.article_count_input.setValue(10)  # Default value
        article_count_layout.addWidget(self.article_count_label)
        article_count_layout.addWidget(self.article_count_input)
        main_layout.addLayout(article_count_layout)

        button_layout = QHBoxLayout()
        self.quit_button = QPushButton("Quit")
        button_layout.addWidget(self.quit_button)
        button_layout.addStretch()
        self.submit_button = QPushButton("Search")
        button_layout.addWidget(self.submit_button)
        main_layout.addLayout(button_layout)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        main_layout.addWidget(self.result_text)

        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

    def get_input(self):
        return self.entry.text()

    def get_article_count(self):
        return self.article_count_input.value()

    def clear_input(self):
        self.entry.clear()

    def set_submit_command(self, command):
        self.submit_button.clicked.connect(command)

    def set_quit_command(self, command):
        self.quit_button.clicked.connect(command)

    def display_results(self, results):
        self.result_text.clear()
        self.result_text.setPlainText(results)

    def mainloop(self):
        self.show()

    def quit(self):
        self.close()