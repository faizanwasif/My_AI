from crewai import Agent, Task, Crew
from langchain_anthropic import ChatAnthropic
from src.utils.agent_tools import get_search_tool

class WebCrawlerModel:
    def __init__(self):
        self.search_tool = get_search_tool()
        self.model = ChatAnthropic(model='claude-3-haiku-20240307')
        self.web_crawl_agent = self._create_web_crawl_agent()
        self.crawling_task = self._create_crawling_task()
        self.crew = self._create_crew()

    def _create_web_crawl_agent(self):
        return Agent(
            role="Researcher",
            goal="Find and summarize the: {info}",
            backstory="""
                You're a researcher at a large company.
                You're responsible for analyzing data and providing insights
                to the business.
            """,
            max_iter=50,
            tools=[self.search_tool],
            llm=self.model,
            allow_delegation=True,
            verbose=True
        )

    def _create_crawling_task(self):
        return Task(
            description="""
                Find the names of the articles on {info} from "https://www.google.com"
                The articles should be only one day old and take out the names of these articles.
            """,
            expected_output="""
                List only 10 newest names of the articles.
            """,
            tools=[self.search_tool],
            agent=self.web_crawl_agent
        )

    def _create_crew(self):
        return Crew(
            agents=[self.web_crawl_agent],
            tasks=[self.crawling_task],
            verbose=True
        )

    def process_input(self, user_input):
        domain_input = {"info": user_input}
        return self.crew.kickoff(inputs=domain_input)