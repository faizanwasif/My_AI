import tkinter as tk
from tkinter import scrolledtext

class AppView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Web Crawler App")
        self._create_widgets()

    def _create_widgets(self):
        self.label = tk.Label(self, text="Enter your search query:")
        self.label.pack()

        self.entry = tk.Entry(self, width=50)
        self.entry.pack()

        self.submit_button = tk.Button(self, text="Search")
        self.submit_button.pack()

        self.result_text = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=60, height=20)
        self.result_text.pack()

        self.quit_button = tk.Button(self, text="Quit")
        self.quit_button.pack()

    def get_input(self):
        return self.entry.get()

    def clear_input(self):
        self.entry.delete(0, tk.END)

    def set_submit_command(self, command):
        self.submit_button.config(command=command)

    def set_quit_command(self, command):
        self.quit_button.config(command=command)

    def display_results(self, results):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, results)