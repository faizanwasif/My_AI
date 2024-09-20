from crewai import Agent, Task, Crew
from langchain_anthropic import ChatAnthropic
from src.utils.agent_tools import URLTool
import config


class WebCrawlerModel:
    def __init__(self):
        self.url_tool = URLTool()
        self.model = ChatAnthropic(model='claude-3-haiku-20240307')
        self.web_crawl_agent = self._create_web_crawl_agent()
        self.crawling_task = self._create_crawling_task()
        self.crew = self._create_crew()
 
    def _create_web_crawl_agent(self):
        return Agent(
            role="Researcher",
            goal="Find relevant sources like articles, blogs and research papers on the topic: {info}.",
            backstory="""
                You are a PhD research assistant at a prestigious university.
                Your primary role involves conducting thorough searches for relevant academic articles, research papers, and scholarly works to support your advisor and research team. 
                You are responsible for gathering, analyzing, and synthesizing academic content, ensuring that the research is grounded in the latest studies and trends in your field. 
                Your work is crucial in aiding the research team's direction and contributing to academic publications.
            """,
            max_iter=10,
            tools=[self.url_tool],
            llm=self.model,
            allow_delegation=True,
            verbose=True
        )
 
    def _create_crawling_task(self):
        return Task(
            description="""
                Extract key-words from {info}.
               
                Search for URLs related to those keywords newest ones only.
                
                YOU MUST REFER TO THE EXAMPLE BELOW!!

                Example:
                Search query:"Search for AI Agentic Systems"
                Keywords:"AI Agentic Systems"
                query:"AI Agentic Systems" 
                 
            
            """,
            expected_output=f"""
                
                List them from newest to oldest.
                The number of articles should ONLY be {config.article_count}
                
                Output "MUST" be structured like the following:
                
                Title: XYZ
                Author: ABC
                Published: YYYY-MM-DD
                Summary: ABCXYZ
                URL: http://arxiv.org/abs/2407.19438v1
                
            """,
            tools=[self.url_tool],
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