import sys
import asyncio
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextBrowser, QSpinBox
from PyQt6.QtCore import QThreadPool, QRunnable, QObject, pyqtSignal, Qt
from PyQt6.QtGui import QTextCursor
from crewai import Agent, Task, Crew
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from agent_tools import ArticleExtractorTool, get_search_tool
import config

class WorkerSignals(QObject):
    result_ready = pyqtSignal(list)
    error = pyqtSignal(str)

class AsyncWorker(QRunnable):
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.func(*self.args, **self.kwargs))
            self.signals.result_ready.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            loop.close()

class WebCrawlerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Web Crawler App")
        self.setGeometry(100, 100, 800, 600)
        self.threadpool = QThreadPool()
        self.articles = []
        self.setup_ui()
        self.setup_web_crawler()

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

        # Quit button layout
        quit_layout = QHBoxLayout()
        quit_layout.addStretch()
        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.quit)
        quit_layout.addWidget(self.quit_button)
        main_layout.addLayout(quit_layout)

        # Results display
        self.result_text = QTextBrowser()
        self.result_text.setOpenExternalLinks(True)  # Allow opening links in external browser
        main_layout.addWidget(self.result_text)

    def setup_web_crawler(self):
        self.url_tool = ArticleExtractorTool()
        self.web_search = get_search_tool()
        self.model = ChatAnthropic(model='claude-3-haiku-20240307')

        self.web_crawl_agent = Agent(
            role="Researcher",
            goal="Find relevant sources like articles, blogs and research papers on the topic: {info}.",
            backstory="""
                You are a PhD research assistant at a prestigious university.
                Your primary role involves conducting thorough searches for relevant academic articles, research papers, and scholarly works to support your advisor and research team. 
                You are responsible for gathering, analyzing, and synthesizing academic content, ensuring that the research is grounded in the latest studies and trends in your field. 
                Your work is crucial in aiding the research team's direction and contributing to academic publications.
            """,
            max_iter=1,
            tools=[self.url_tool],
            llm=self.model,
            allow_delegation=False,
            verbose=True
        )

        self.crawling_task = Task(
            description="Search for relevant articles on the given topic using the Article Extractor Tool.",
            expected_output="A list of relevant articles with their titles, summaries, and links.",
            tools=[self.url_tool],
            agent=self.web_crawl_agent
        )

        self.crew = Crew(
            agents=[self.web_crawl_agent],
            tasks=[self.crawling_task],
            verbose=True
        )

    def submit(self):
        user_input = self.entry.text()
        self.entry.clear()
        config.article_count = self.article_count_input.value()
        
        self.result_text.setHtml("Searching for articles... Please wait.")
        
        worker = AsyncWorker(self.process_input, user_input)
        worker.signals.result_ready.connect(self.display_results)
        worker.signals.error.connect(self.handle_error)
        self.threadpool.start(worker)

    async def process_input(self, user_input):
        return await self.url_tool._arun(user_input)

    def display_results(self, results):
        self.articles = results
        if not self.articles:
            self.result_text.setHtml("No results found. Please try a different search query.")
            return

        self.search_articles()  # Display all articles initially

    def search_articles(self):
        search_query = self.article_search_entry.text().lower()
        filtered_articles = [article for article in self.articles if self.article_matches_search(article, search_query)]

        html_content = "<html><body>"
        for article in filtered_articles:
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

    def article_matches_search(self, article, search_query):
        if not search_query:
            return True
        return any(search_query in str(value).lower() for value in article.values())

    def handle_error(self, error_message):
        print(f"Error occurred: {error_message}")
        self.result_text.setHtml(f"<p style='color: red;'>An error occurred: {error_message}</p>")

    def quit(self):
        self.close()

def main():
    load_dotenv()
    app = QApplication(sys.argv)
    window = WebCrawlerApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()