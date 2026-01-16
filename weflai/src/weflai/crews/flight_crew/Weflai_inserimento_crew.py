from typing import List
from crewai import Agent, Crew, Process, Task,LLM
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
# from dotenv import load_dotenv
# load_dotenv()

#Tool utilizzati da crewAI riguardo i database
from langchain_community.utilities.sql_database import SQLDatabase
from crewai.tools import tool
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLCheckerTool,
    QuerySQLDatabaseTool
)



db = SQLDatabase.from_uri(database_uri = "postgresql://chri00:rudogachia@localhost:5432/postgres", 
                          schema='public', 
                          engine_args={"isolation_level": "AUTOCOMMIT"})

llm = LLM (
    model = "ollama/llama3.1:8b",
    base_url="http://localhost:11434"
)


@tool("list_tables")
def list_tables_tool() -> str:
    """List the available tables in the PostgreSQL database"""
    return ListSQLDatabaseTool(db=db).invoke("")

@tool("tables_schema")
def tables_schema_tool(table_names: str) -> str:
    """
    Get the schema of specific tables.
    Input should be a comma-separated list of table names.
    """
    return InfoSQLDatabaseTool(db=db).invoke(table_names)

@tool("execute_sql")
def execute_sql_tool(query: str) -> str:
    """Execute a SQL query on the PostgreSQL database"""
    return QuerySQLDatabaseTool(db=db).invoke(query)

@tool("check_sql")
def check_sql_tool(sql_query:str) -> str:
    """ Check if the SQL query is correct. Returns suggestions/fixes or succes message"""
    try:
        llm_checker = ollama_llm
        query_checker_tool = QuerySQLCheckerTool(db=db, llm=llm_checker)
        return query_checker_tool.invoke({"query":sql_query})
    except Exception as e:
        return f"Error using QuerySQLCheckerTool: {str(e)}"

@CrewBase
class InserimentoCrew():
    """Inserimento Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    
    agents_config = "config/agents.yaml"
    tasks_inserimento_config = "config/tasks_inserimento.yaml"

    
    @agent
    def flight_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['flight_analyst'],
            tools=[list_tables_tool, tables_schema_tool, execute_sql_tool], #assegnati tool di lettura
            llm=llm,
            verbose=True,
            
        )
    @agent
    def booking_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['booking_manager'],
            tools=[check_sql_tool,execute_sql_too], #assegnati tool di scrittura
            llm=llm,
            verbose=True,
            
        )
    @agent
    def customer_experience_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['customer_experience_agent'],
            tools=[], 
            llm=ollama_llm,
            verbose=True,
            
        )

    @task
    def search_flight_task(self) -> Task:
        return Task(
            config=self.tasks_config["search_flight_task"],  # type: ignore[index]
        )
    @task
    def insert_booking_task(self) -> Task:
        return Task(
            config=self.tasks_config["insert_booking_task"],  # type: ignore[index]
        )
    @task
    def generate_JSON_ticket_task(self) -> Task:
        return Task(
            config=self.tasks_config["generate_JSON_ticket_task"],  # type: ignore[index]
        )
    
    
    @crew
    def crew(self) -> Crew:
        """Creates the Research Crew"""
        return Crew(
            agents=self.agents,  #decoratore che importa tutti gli agenti definiti con @agent
            tasks=self.tasks,  #decoratore che importa tutte le task definite con @task
            process=Process.sequential,
            verbose=True,
        )
