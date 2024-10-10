from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextBrowser, QSpinBox # type: ignore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor

class MainWindow(QMainWindow):
    def __init__(self, web_crawler, article_model):
        super().__init__()
        self.web_crawler = web_crawler
        self.article_model = article_model
        self.setWindowTitle("Web Crawler App")
        self.setGeometry(100, 100, 800, 600)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Search query layout
        search_layout = QHBoxLayout()
        self.label = QLabel("Enter your search query:")
        search_layout.addWidget(self.label)
        self.entry = QLineEdit()
        search_layout.addWidget(self.entry)
        self.submit_button = QPushButton("Search")
        self.submit_button.clicked.connect(self.submit)
        search_layout.addWidget(self.submit_button)
        main_layout.addLayout(search_layout)

        # Article count layout
        article_count_layout = QHBoxLayout()
        self.article_count_label = QLabel("Number of articles:")
        self.article_count_input = QSpinBox()
        self.article_count_input.setMinimum(1)
        self.article_count_input.setMaximum(100)
        self.article_count_input.setValue(10)  # Default value
        article_count_layout.addWidget(self.article_count_label)
        article_count_layout.addWidget(self.article_count_input)
        article_count_layout.addStretch()
        main_layout.addLayout(article_count_layout)

        # Article search layout
        article_search_layout = QHBoxLayout()
        self.article_search_label = QLabel("Search within articles:")
        article_search_layout.addWidget(self.article_search_label)
        self.article_search_entry = QLineEdit()
        self.article_search_entry.textChanged.connect(self.search_articles)
        article_search_layout.addWidget(self.article_search_entry)
        main_layout.addLayout(article_search_layout)

        # New Article Generator Button
        new_topic_suggester_layout = QHBoxLayout()
        self.new_topic_suggester_button = QPushButton("Suggest New Topic")
        self.new_topic_suggester_button.clicked.connect(self.suggest_new_topic)
        new_topic_suggester_layout.addWidget(self.new_topic_suggester_button)
        main_layout.addLayout(new_topic_suggester_layout)

        # Quit button layout
        quit_layout = QHBoxLayout()
        quit_layout.addStretch()
        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close)
        quit_layout.addWidget(self.quit_button)
        main_layout.addLayout(quit_layout)

        # Results display
        self.result_text = QTextBrowser()
        self.result_text.setOpenExternalLinks(True)  # Allow opening links in external browser
        main_layout.addWidget(self.result_text)

    def submit(self):
        user_input = self.entry.text()
        self.entry.clear()
        article_count = self.article_count_input.value()
        
        self.result_text.setHtml("Searching for articles... Please wait.")
        
        self.web_crawler.search_articles(user_input, article_count, self.display_results, self.handle_error)

    def search_articles(self):
        search_query = self.article_search_entry.text().lower()
        filtered_articles = self.article_model.search_articles(search_query)
        self.display_results(filtered_articles)

    def suggest_new_topic(self):
        user_input = self.entry.text()
        if not user_input:
            user_input = "recent trends in technology"  # Default input if the entry is empty
        self.result_text.setHtml("Suggesting new topics... Please wait.")
        self.web_crawler.suggest_new_topic(user_input, self.display_topic_suggestions, self.handle_error)

    def display_results(self, articles):
        if not articles:
            self.result_text.setHtml("No results found. Please try a different search query.")
            return

        html_content = "<html><body>"
        for article in articles:
            html_content += f"<h3>{article.get('title', 'N/A')}</h3>"
            html_content += f"<p><strong>Author:</strong> {article.get('author', 'N/A')}</p>"
            html_content += f"<p><strong>Published:</strong> {article.get('published', 'N/A')}</p>"
            html_content += f"<p><strong>Source:</strong> {article.get('source', 'N/A')}</p>"
            
            link = article.get('link', 'N/A')
            if link != 'N/A':
                html_content += f'<p><strong>Link:</strong> <a href="{link}">{link}</a></p>'
            else:
                html_content += f"<p><strong>Link:</strong> {link}</p>"
            
            html_content += f"<p><strong>Summary:</strong> {article.get('summary', 'N/A')}</p>"
            html_content += "<hr>"

        html_content += "</body></html>"
        self.result_text.setHtml(html_content)
        
        # Scroll to the top
        self.result_text.moveCursor(QTextCursor.MoveOperation.Start)
    

    def display_topic_suggestions(self, topics):
        html_content = "<html><body>"
        html_content += "<h2>Suggested Research Topics:</h2>"

        # Iterate over each topic in the list and add numbering, title, and description
        for idx, topic in enumerate(topics, start=1):
            html_content += f"<h3>{idx}. {topic['title']}</h3>"  # Display title as a heading
            html_content += f"<p>{topic['description']}</p>"  # Display description in a paragraph
            html_content += "<br>"  # Add space between topics for readability

        html_content += "<hr>"
        html_content += "</body></html>"

        self.result_text.setHtml(html_content)
        self.result_text.moveCursor(QTextCursor.MoveOperation.Start)



    def handle_error(self, error_message):
        print(f"Error occurred: {error_message}")
        self.result_text.setHtml(f"<p style='color: red;'>An error occurred: {error_message}</p>")