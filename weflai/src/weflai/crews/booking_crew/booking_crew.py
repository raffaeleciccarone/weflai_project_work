from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
# Assicurati che questi import puntino ai tuoi file reali
from weflai.tools.db_tools import execute_sql_tool 
from weflai.models import TicketOutput

@CrewBase
class BookingCrew():
    """Booking Crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks_booking.yaml'

    # LLM Configuration
    ollama_llm = LLM(
        model="ollama/llama3.1:8b",
        base_url="http://localhost:11434"
    )

    @agent
    def flight_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['flight_analyst'],
            # RIMOSSO: tables_schema_tool e list_tables_tool. 
            # Ha già lo schema nella backstory, non deve perdere tempo a cercarlo.
            tools=[execute_sql_tool], 
            llm=self.ollama_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def booking_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['booking_manager'],
            tools=[execute_sql_tool],
            llm=self.ollama_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def customer_experience_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['customer_experience_agent'],
            tools=[execute_sql_tool],
            llm=self.ollama_llm,
            verbose=True,
            allow_delegation=False
        )

    @task
    def search_flight_task(self) -> Task:
        return Task(config=self.tasks_config['search_flight_task'])

    @task
    def confirm_selection_task(self) -> Task:
        return Task(
            config=self.tasks_config['confirm_selection_task'],
            agent=self.flight_analyst(),
            human_input=True,
            # Questo assicura che l'input umano sia l'unica cosa che conta qui
    )

    @task
    def insert_booking_task(self) -> Task:
        return Task(
            config=self.tasks_config['insert_booking_task'],
            # Il contesto è fondamentale qui per passare l'ID volo e la conferma
            context=[self.search_flight_task(), self.confirm_selection_task()]
        )

    @task
    def generate_JSON_ticket_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_JSON_ticket_task'],
            context=[self.insert_booking_task()], # Gli serve solo l'ID prenotazione
            output_pydantic=TicketOutput,
            output_file='ticket_emesso.json'
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.flight_analyst(), self.booking_manager(), self.customer_experience_agent()],
            tasks=[
                self.search_flight_task(), 
                self.confirm_selection_task(), 
                self.insert_booking_task(), 
                self.generate_JSON_ticket_task()
            ],
            process=Process.sequential,
            verbose=True
        )