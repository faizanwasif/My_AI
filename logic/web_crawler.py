import asyncio
from PyQt6.QtCore import QThreadPool, QRunnable, QObject, pyqtSignal 
from crewai import Agent, Task, Crew 
from langchain_anthropic import ChatAnthropic
from agent_tools import ArticleExtractorTool, get_search_tool
import config
import json

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
    model = ChatAnthropic(model='claude-3-haiku-20240307')
    
    def __init__(self, article_model):
        self.article_model = article_model
        self.threadpool = QThreadPool()
        self.setup_web_crawler()
        self.setup_new_topic_suggester_agent()
        # self.run_crew()

    def setup_web_crawler(self):
        self.url_tool = ArticleExtractorTool()
        self.web_search = get_search_tool()

        self.web_crawl_agent = Agent(
            role="Researcher",
            goal="Find relevant sources like articles, blogs and research papers on the given topic.",
            backstory="""
                You are a PhD research assistant at a prestigious university.
                Your primary role involves conducting thorough searches for relevant academic articles, research papers, and scholarly works to support your advisor and research team. 
                You are responsible for gathering, analyzing, and synthesizing academic content, ensuring that the research is grounded in the latest studies and trends in your field. 
                Your work is crucial in aiding the research team's direction and contributing to academic publications.
            """,
            max_iter=1,
            tools=[self.url_tool],
            llm=WebCrawler.model,
            allow_delegation=False,
            verbose=True
        )

        self.crawling_task = Task(
            description="Search for relevant articles on the given topic using the Article Extractor Tool.",
            expected_output="A list of relevant articles with their titles, summaries, and links.",
            tools=[self.url_tool],
            agent=self.web_crawl_agent
        )

    def setup_new_topic_suggester_agent(self):
        self.topic_suggester_agent = Agent(
            role="Expert Research Topic Suggester",
            goal="Analyze the provided {articles} and suggest new, unique research topics in a structured format.",
            backstory="""
                You are a highly experienced PhD research assistant at a prestigious university.
                Your expertise lies in identifying innovative research topics based on current trends and literature.
                Your primary role involves suggesting well-structured research topics to your advisor and research team.
                You generate a list of relevant topics with clear titles and detailed descriptions of their significance and potential impact.
                Your structured and detailed suggestions are crucial in guiding the research team's direction and contributing to high-impact academic publications.
            """,
            max_iter=1,
            tools=[],
            llm=WebCrawler.model,
            allow_delegation=False,
            verbose=True
        )

        self.topic_suggester_task = Task(
            description="""
                Analyze the provided list of {articles} and based on this list suggest 5 new, unique research topics in this area.
                Each topic should be provided in a structured format as a dictionary with 'title' and 'description' keys.
                The 'title' should be a concise, descriptive heading of the research topic.
                The 'description' should be a brief explanation of the topic's significance and potential impact.
                Output the result as a JSON-formatted list of dictionaries.
            """,
            expected_output="""
                A dictionary, each containing:
                - 'title': A concise, descriptive heading of the research topic.
                - 'description': A brief explanation of the topic's significance and potential impact.
                
            """,
            tools=[],
            agent=self.topic_suggester_agent
        )


    # def run_crew(self):
        # self.crew = Crew(
        #     agents=[self.web_crawl_agent, self.topic_suggester_agent],
        #     tasks=[self.crawling_task, self.topic_suggester_task],
        #     verbose=True
        # )

    def search_articles(self, user_input, article_count, success_callback, error_callback):
        config.article_count = article_count
        worker = AsyncWorker(self.process_input, user_input, is_article_search=True)
        worker.signals.result_ready.connect(self.handle_results)
        worker.signals.result_ready.connect(success_callback)
        worker.signals.error.connect(error_callback)
        self.threadpool.start(worker)

    def suggest_new_topic(self, user_input, success_callback, error_callback):
        worker = AsyncWorker(self.process_input, user_input, is_article_search=False)
        worker.signals.result_ready.connect(success_callback)
        worker.signals.error.connect(error_callback)
        self.threadpool.start(worker)

    async def process_input(self, user_input, is_article_search):
        # First, use the web crawler to find articles
        articles = await self.url_tool._arun(user_input)
        self.handle_results(articles)

        self.crew = Crew(
            agents=[self.topic_suggester_agent],
            tasks=[self.topic_suggester_task],
            verbose=True
        )

        if is_article_search:
            return articles
        else:
            # Prepare a summary of the articles for the topic suggester
            article_summaries = "\n".join([f"Title: {art['title']}" for art in articles])
            print(f"Article Summaries: {article_summaries}")
            
            # Use the topic suggester to generate new topics based on the article summaries
            result = self.crew.kickoff({"articles": article_summaries})

            # Parse the JSON-formatted string into a Python list of dictionaries
            topics = json.loads(result)

            # print(f"Result: {topics}")
            # print(f"Result type: {type(topics)}")  # Should now be <class 'list'>

            return topics

    def handle_results(self, results):
        self.article_model.set_articles(results)