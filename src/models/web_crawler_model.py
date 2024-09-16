from crewai import Agent, Task, Crew
from langchain_anthropic import ChatAnthropic
from src.utils.agent_tools import URLTool
from langchain_openai import ChatOpenAI

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
<<<<<<< Updated upstream
            goal="""Find relevant sources like articles, blogs and research papers on the topic: {info} """,
=======
            goal="Find relevant sources like articles, blogs and research papers on the topic: {info}. Use DuckDuckGo to search for the most relevant articles, blogs, or sources.",
>>>>>>> Stashed changes
            backstory="""
                You are a PhD research assistant at a prestigious university.
                Your primary role involves conducting thorough searches for relevant academic articles, research papers, and scholarly works to support your advisor and research team. 
                You are responsible for gathering, analyzing, and synthesizing academic content, ensuring that the research is grounded in the latest studies and trends in your field. 
                Your work is crucial in aiding the research team’s direction and contributing to academic publications.
            """,
            max_iter=20,
<<<<<<< Updated upstream
            tools=[self.url_tool],
=======
            tools=[self.search_tool],
>>>>>>> Stashed changes
            llm=self.model,
            allow_delegation=True,
            verbose=True
        )
 
    def _create_crawling_task(self):
        
         return Task(
            
            description="""

<<<<<<< Updated upstream
                Extract key-words from {info}.
               
                Search for URls related to those keywords by adding a + symbol between all the keywords.
                
                Example:
                Search query:"Search for AI Agentic Systems"
                Keywords:"AI Agentic Systems"
                query:"AI+Agentic+Systems"
                 
                
 
            """,
            expected_output="""
               
               
              
                Provide a list URLs of most relevant articles.
=======
                Search for articles related to "{info}" using "https://www.google.com". 
                The articles should be the newest and most relevant based on the topic provided.

            """,
            expected_output="""
                Provide exact title of the research papers and articles that are the most relevant to the topic provided.
                Provide their summery as well.
                Provide a list of only 10 most relevant articles and their summery.
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream

      
#     Task(
    
#     description="""

#         Search for articles related to "{info}" using "https://www.google.com" on "https://arxiv.org"
#         The articles should be the newest and most relevant based on the topic provided.

#     """,
#     expected_output="""
#         Provide exact title of the research papers and articles that are the most relevant to the topic provided.
#         provide "exact URL" link to that research paper and article.
#         Provide their summary as well.
#         Provide a list of most relevant articles and their summary.
#     """,
#     tools=[self.search_tool],
#     agent=self.web_crawl_agent
# )
=======
    
>>>>>>> Stashed changes
