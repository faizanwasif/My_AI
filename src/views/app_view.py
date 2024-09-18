import tkinter as tk
from tkinter import scrolledtext, ttk

class AppView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Web Crawler App")
        self.geometry("800x600")  # Increased window size
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.label = ttk.Label(main_frame, text="Enter your search query:")
        self.label.pack(pady=(0, 5))

        self.entry = ttk.Entry(main_frame, width=80)  # Increased entry width
        self.entry.pack(pady=(0, 10), fill=tk.X)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        self.submit_button = ttk.Button(button_frame, text="Search")
        self.submit_button.pack(side=tk.LEFT, padx=(0, 10))

        self.quit_button = ttk.Button(button_frame, text="Quit")
        self.quit_button.pack(side=tk.RIGHT)

        self.result_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=80, height=30)  # Increased text area size
        self.result_text.pack(fill=tk.BOTH, expand=True)

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