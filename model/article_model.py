class ArticleModel:
    def __init__(self):
        self.articles = []

    def set_articles(self, articles):
        self.articles = articles

    def search_articles(self, search_query):
        if not search_query:
            return self.articles
        return [article for article in self.articles if self.article_matches_search(article, search_query)]

    def article_matches_search(self, article, search_query):
        return any(search_query in str(value).lower() for value in article.values())
    