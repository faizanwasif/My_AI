import asyncio
from crewai import Agent, Task, Crew
from langchain_anthropic import ChatAnthropic
from src.utils.agent_tools import ArticleExtractorTool, get_search_tool
import config

class WebCrawlerModel:
    def __init__(self):
        self.url_tool = ArticleExtractorTool()
        self.web_search = get_search_tool()
        
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
                Instructions:

                    Given the input {info}, perform the following steps:

                    Correct any errors (e.g., spelling, grammar) in {info}.
                    Extract the main keywords from the corrected input.
                    Formulate a search query based on the keywords.
                    Search for the newest URLs related to these keywords.
                    Your output should follow this format:

                    Search Query: "corrected input"
                    Keywords: "extracted keywords"
                    Query: "search query"
                
                Example:

                    Search Query: "Search for AI Agentic Systems"
                    Keywords: "AI Agentic Systems"
                    Query: "AI Agentic Systems"
            """,
            expected_output=f"""
                Output "MUST" be structured like the following:
                
                Title: XYZ
                Author: ABC
                Published: YYYY-MM-DD
                URL/Link: http://hhhhjjjkkkklmnop
                Summary: ABCXYZ                
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

    async def process_input(self, user_input):
        domain_input = {"info": user_input}
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.crew.kickoff, domain_input)

# Async initialization function
async def create_web_crawler_model():
    model = WebCrawlerModel()
    return model

# Usage example
async def main():
    model = await create_web_crawler_model()
    result = await model.process_input("Your search query here")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())