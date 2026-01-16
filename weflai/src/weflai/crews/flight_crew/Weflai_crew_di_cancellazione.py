import os
from typing import List
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from langchain_community.utilities.sql_database import SQLDatabase
from crewai.tools import tool
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLCheckerTool,
    QuerySQLDatabaseTool
)

#config. DB
db = SQLDatabase.from_uri(database_uri = "postgresql://Joe:1234@localhost:5432/postgres", 
                          schema='We_FlAI')

#config. LLM
llm = LLM (
    model = "ollama/llama3.1:8b",
    base_url="http://localhost:11434"
)

#config. Tools
@tool("list_tables")
def list_tables_tool() -> str:
    """List the available tables in the DB."""
    return ListSQLDatabaseTool(db=db).invoke("")

@tool("tables_schema")
def tables_schema_tool(tables: str) -> str:
    """Show schema & sample rows for the given tables (comma-separated)."""
    return InfoSQLDatabaseTool(db=db).invoke(tables)

@tool("execute_sql")
def execute_sql_tool(sql_query: str) -> str:
    """Execute a SQL query against the DB. Returns the result as a string."""
    return QuerySQLDatabaseTool(db=db).invoke(sql_query)

@tool("check_sql")
def check_sql_tool(sql_query: str) -> str:
    """Check if the SQL query is correct. Returns suggestions/fixes or success message."""
    try:
        llm_checker = llm
        query_checker_tool = QuerySQLCheckerTool(db=db, llm=llm_checker)
        return query_checker_tool.invoke({"query": sql_query})
    except Exception as e:
        return f"Error using QuerySQLCheckerTool: {str(e)}"

#config. Agents e Tasks
@CrewBase
class CancellazioneCrew():

    agents: List[BaseAgent]
    tasks: List[Task]

    
    agents_config = "config/agents.yaml"
    tasks_cancellazione_config = "config/tasks_cancellazione.yaml"

    #definizione degli agenti
    @agent
    def flight_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['flight_analyst'],
            llm=llm,
            verbose=True,
            tools=[list_tables_tool, tables_schema_tool, execute_sql_tool]
        )
    @agent
    def booking_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['booking_manager'],
            llm=llm,
            verbose=True,
            tools=[check_sql_tool, execute_sql_tool]
        )

    #definizione delle task
    @task
    def find_booking_to_cancel_task(self) -> Task:
        return Task(
            config=self.tasks_config["find_booking_to_cancel_task"],
        )

    @task
    def delete_booking_task(self) -> Task:
        return Task(
            config=self.tasks_config["delete_booking_task"],
        )
    
    #definizione della crew di cancellazione
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents, 
            tasks=self.tasks,   
            process=Process.sequential,
            verbose=True,
        )
