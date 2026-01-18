from crewai import Agent, Crew, Process, Task,LLM
from crewai.project import CrewBase, agent, crew, task
# Importiamo sia DB tool che RAG tool
from weflai.tools.db_tools import execute_sql_tool, list_tables_tool
from weflai.tools.rag_tools import pdf_tool

@CrewBase
class InfoCrew():
    """Info & RAG Crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks_info.yaml'

    # --- 1. DEFINISCI L'LLM QUI ---
    ollama_llm = LLM(
        model="ollama/llama3.1:8b",
        base_url="http://localhost:11434"
    )

    @agent
    def info_rag_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['info_rag_agent'],
            # Questo agente ha accesso a entrambi i mondi (DB e PDF)
            tools=[execute_sql_tool, list_tables_tool, pdf_tool],
            llm=self.ollama_llm,
            verbose=True
        )

    @task
    def answer_info_task(self) -> Task:
        return Task(config=self.tasks_config['answer_info_task'])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.info_rag_agent()],
            tasks=[self.answer_info_task()],
            verbose=True
        )