import aiohttp
import asyncio
import json
import feedparser
import config
from datetime import datetime
from langchain.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchRun

def get_search_tool():
    return DuckDuckGoSearchRun()

class ArticleExtractorTool(BaseTool):
    name: str = "Asynchronous Combined Article Extractor Tool"
    description: str = "This tool asynchronously extracts articles from both arXiv and OpenAlex based on a search query."

    async def _arun(self, query: str) -> list:
        async with aiohttp.ClientSession() as session:
            arxiv_task = asyncio.create_task(self._fetch_arxiv_articles(session, query))
            openalex_task = asyncio.create_task(self._fetch_openalex_articles(session, query))
            
            arxiv_results, openalex_results = await asyncio.gather(arxiv_task, openalex_task)
        
        # Combine results, alternating between sources
        combined_results = []
        for arxiv, openalex in zip(arxiv_results, openalex_results):
            combined_results.append(arxiv)
            combined_results.append(openalex)
        
        # Add any remaining results
        combined_results.extend(arxiv_results[len(openalex_results):])
        combined_results.extend(openalex_results[len(arxiv_results):])
        
        return combined_results[:config.article_count]  # Limit to the requested number of articles

    async def _fetch_arxiv_articles(self, session: aiohttp.ClientSession, query: str) -> list:
        result = query.replace(" ", "+")
        base_url = "http://export.arxiv.org/api/query?"
        search_query = f"search_query=all:{result}&start=0&max_results={config.article_count}&sortOrder=descending"
        url = base_url + search_query
        
        async with session.get(url) as response:
            data = await response.text()
        
        feed = feedparser.parse(data)
        
        results = []
        for entry in feed.entries:
            result = {
                'title': entry.title,
                'summary': entry.summary,
                'published': entry.published,
                'link': entry.link,
                'author': entry.author,
                'source': 'arXiv'
            }
            results.append(result)
        
        return results

    async def _fetch_openalex_articles(self, session: aiohttp.ClientSession, query: str) -> list:
        base_url = "https://api.openalex.org/works"
        current_year = datetime.now().year
        params = {
            'filter': f'title.search:{query},publication_year:2010-{current_year}',
            'sort': 'publication_date:desc',
            'per_page': config.article_count
        }
        
        async with session.get(base_url, params=params) as response:
            data = await response.json()
        
        results = []
        for work in data.get('results', []):
            result = {
                'title': work.get('title'),
                'summary': work.get('abstract'),
                'published': work.get('publication_date'),
                'link': work.get('doi'),
                'author': work.get('authorships', [{}])[0].get('author', {}).get('display_name', 'N/A'),
                'source': 'OpenAlex'
            }
            results.append(result)
        
        return results

    def _run(self, query: str) -> list:
        return asyncio.run(self._arun(query))