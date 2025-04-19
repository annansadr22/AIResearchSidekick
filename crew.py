import os
from dotenv import load_dotenv
from crewai import Crew, Task
from crewai.agent import CrewAgent
#from crewai import Crew, Task, CrewAgent
from serper_tool import SerperDevTool
from gemini_tool import gemini_summarize
#from fake_llm import FakeLLM



load_dotenv()
search_tool = SerperDevTool(api_key=os.getenv("SERPER_API_KEY"))

# Define agents
def load_agents():
    search_agent = CrewAgent(
        role="Web Researcher",
        goal="Search online for relevant information",
        backstory="Expert in Serper search.",
        verbose=True,
        process=lambda query: SerperDevTool().run(query)
    )

    summarizer_agent = CrewAgent(
        role="Summarizer",
        goal="Summarize findings clearly",
        backstory="Skilled at summarizing using Gemini",
        verbose=True,
        process=lambda context: gemini_summarize(f"Summarize this:\n{context}")
    )

    return {
        "search_agent": search_agent,
        "summarizer_agent": summarizer_agent
    }


# Define task flow
def load_tasks(query: str):
    agents = load_agents()
    return [
        Task(description=f"Search online for: {query}", agent=agents["search_agent"]),
        Task(description=f"Summarize findings about: {query}", agent=agents["summarizer_agent"]),
    ]

# Run the agents
def run_agents(query: str):
    crew = Crew(
        agents=list(load_agents().values()),
        tasks=load_tasks(query),
        verbose=True
    )
    return crew.kickoff()
