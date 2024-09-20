from langchain_community.tools import DuckDuckGoSearchRun
import urllib.request
import feedparser
from crewai_tools import tool
from crewai_tools import BaseTool
import config


def get_search_tool():
    return DuckDuckGoSearchRun()

class URLTool(BaseTool):
    name: str ="URL extractor tool"
    description: str = ("This tool will return URLs")
    
    def _run(self, query: str) -> list:
         # Construct the arXiv API URL
         
        base_url = "http://export.arxiv.org/api/query?"
        search_query = f"search_query=all:{query}&start={0}&max_results={config.article_count}"
        url = base_url + search_query
        
        # Make the API request
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
        
        # Parse the Atom feed
        feed = feedparser.parse(data)
        
        # Extract and print the results
        results = []
        for entry in feed.entries:
            result = {
                'title': entry.title,
                'summary': entry.summary,
                'published': entry.published,
                'link': entry.link,
                'author': entry.author
            }
            results.append(result)
        
        return results
