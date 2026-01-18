from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from weflai.tools.db_tools import execute_sql_tool

@CrewBase
class CancellationCrew():
    """Cancellation Crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks_cancellation.yaml'

    ollama_llm = LLM(
        model="ollama/llama3.1:8b",
        base_url="http://localhost:11434"
    )

    @agent
    def flight_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['flight_analyst'],
            tools=[execute_sql_tool], # Anche qui, niente schema tool
            llm=self.ollama_llm,
            verbose=True
        )

    @agent
    def booking_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['booking_manager'],
            tools=[execute_sql_tool],
            llm=self.ollama_llm,
            verbose=True
        )

    @task
    def find_booking_to_cancel_task(self) -> Task:
        return Task(config=self.tasks_config['find_booking_to_cancel_task'])

    @task
    def delete_booking_task(self) -> Task:
        return Task(
            config=self.tasks_config['delete_booking_task'],
            context=[self.find_booking_to_cancel_task()] # Fondamentale per ricevere l'ID
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.flight_analyst(), self.booking_manager()],
            tasks=[self.find_booking_to_cancel_task(), self.delete_booking_task()],
            process=Process.sequential,
            verbose=True
        )