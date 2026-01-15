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

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

db = SQLDatabase.from_uri(database_uri = "postgresql://chri00:rudogachia@localhost:5432/postgres", 
                          schema='public', 
                          engine_args={"isolation_level": "AUTOCOMMIT"})

ollama_llm = LLM (
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
class PoemCrew:
    """Poem Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # If you would lik to add tools to your crew, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools

    
    @agent
    def poem_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["poem_writer"],  # type: ignore[index]
            llm = ollama_llm
        )
        

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def write_poem(self) -> Task:
        return Task(
            config=self.tasks_config["write_poem"],  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Research Crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
