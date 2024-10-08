import sys
from PyQt6.QtWidgets import QApplication
from dotenv import load_dotenv
from ui.main_window import MainWindow
from logic.web_crawler import WebCrawler
from model.article_model import ArticleModel

def main():
    load_dotenv()
    app = QApplication(sys.argv)
    
    article_model = ArticleModel()
    web_crawler = WebCrawler(article_model)
    window = MainWindow(web_crawler, article_model)
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()