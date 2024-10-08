import asyncio
from PyQt6.QtCore import QThreadPool, QRunnable, QObject, pyqtSignal
from crewai import Agent, Task, Crew
from langchain_anthropic import ChatAnthropic
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

class WebCrawler:
    def __init__(self, article_model):
        self.article_model = article_model
        self.threadpool = QThreadPool()
        self.setup_web_crawler()

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

    def search_articles(self, user_input, article_count, success_callback, error_callback):
        config.article_count = article_count
        worker = AsyncWorker(self.process_input, user_input)
        worker.signals.result_ready.connect(self.handle_results)
        worker.signals.result_ready.connect(success_callback)
        worker.signals.error.connect(error_callback)
        self.threadpool.start(worker)

    async def process_input(self, user_input):
        return await self.url_tool._arun(user_input)

    def handle_results(self, results):
        self.article_model.set_articles(results)