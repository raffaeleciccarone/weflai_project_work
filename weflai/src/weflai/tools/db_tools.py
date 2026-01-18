from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.tools.sql_database.tool import (
    ListSQLDatabaseTool,
    InfoSQLDatabaseTool,
    QuerySQLDatabaseTool,
    QuerySQLCheckerTool
)
from crewai.tools import tool
from crewai import LLM
import logging

# Setup logging per debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
db = SQLDatabase.from_uri(
    database_uri="postgresql://chri00:rudogachia@localhost:5432/postgres", 
    schema="We_FlAI", 
    engine_args={"isolation_level": "AUTOCOMMIT"}
)

ollama_llm = LLM(
    model="ollama/llama3.1:8b",
    base_url="http://localhost:11434"
)

@tool("list_tables_tool")
def list_tables_tool() -> str:
    """
    Lista le tabelle disponibili nello schema We_FlAI.
    Output: Lista di nomi tabelle separati da virgola.
    """
    try:
        result = ListSQLDatabaseTool(db=db).run("")
        logger.info(f"✓ Tabelle trovate: {result}")
        return result
    except Exception as e:
        error_msg = f"ERRORE list_tables: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool("tables_schema_tool")
def tables_schema_tool(table_names: str | list) -> str:
    """
    Ottiene lo schema (colonne e tipi) delle tabelle specificate.
    
    Input:
    - String: "We_FlAI.Voli" oppure "We_FlAI.Voli, We_FlAI.Aeroporti"
    - List: ["We_FlAI.Voli", "We_FlAI.Aeroporti"]
    
    Output: Schema dettagliato con nomi colonne e tipi di dato.
    """
    try:
        # Normalizza input
        if isinstance(table_names, list):
            table_names = ", ".join(table_names)
        
        # Forza schema prefix se mancante
        if "We_FlAI" not in table_names:
            tables = [f'"We_FlAI"."{t.strip()}"' for t in table_names.split(",")]
            table_names = ", ".join(tables)
        
        result = InfoSQLDatabaseTool(db=db).run(table_names)
        logger.info(f"✓ Schema recuperato per: {table_names}")
        return result
    except Exception as e:
        error_msg = f"ERRORE tables_schema: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool("execute_sql_tool")
def execute_sql_tool(query: str) -> str:
    """
    Esegue una query SQL sul database PostgreSQL.
    
    ATTENZIONE:
    - Usa SEMPRE i doppi apici per le colonne: "DataPTZ", NON dataptz
    - Schema esplicito: "We_FlAI"."Voli", NON solo Voli
    - Per INSERT usa RETURNING per ottenere l'ID generato
    
    Input: Query SQL completa
    Output: Risultato query o messaggio di errore
    """
    try:
        # Log query prima dell'esecuzione (per debug)
        logger.info(f"🔄 Esecuzione query:\n{query}")
        
        # Validazione base
        if not query.strip():
            return "ERRORE: Query vuota"
        
        # Esecuzione
        result = QuerySQLDatabaseTool(db=db).run(query)
        
        # Log risultato
        logger.info(f"✓ Query eseguita con successo. Risultato:\n{result}")
        return result
        
    except Exception as e:
        error_msg = f"ERRORE execute_sql: {str(e)}\nQuery: {query}"
        logger.error(error_msg)
        
        # Suggerimenti contestuali
        if "column" in str(e).lower() and "does not exist" in str(e).lower():
            error_msg += "\n\n⚠️ SUGGERIMENTO: Hai dimenticato i doppi apici? Es: \"DataPTZ\" invece di dataptz"
        elif "relation" in str(e).lower() and "does not exist" in str(e).lower():
            error_msg += "\n\n⚠️ SUGGERIMENTO: Usa il prefisso schema: \"We_FlAI\".\"Voli\""
        elif "syntax error" in str(e).lower():
            error_msg += "\n\n⚠️ SUGGERIMENTO: Controlla apostrofi nei nomi (usa '' per escape)"
        
        return error_msg

@tool("check_sql_tool")
def check_sql_tool(sql_query: str) -> str:
    """
    Verifica la correttezza sintattica di una query SQL prima dell'esecuzione.
    
    Input: Query SQL da validare
    Output: Messaggio di successo o suggerimenti di correzione
    """
    try:
        llm_checker = ollama_llm
        query_checker_tool = QuerySQLCheckerTool(db=db, llm=llm_checker)
        result = query_checker_tool.run({"query": sql_query})
        logger.info(f"✓ Query validata: {result}")
        return result
    except Exception as e:
        error_msg = f"ERRORE check_sql: {str(e)}"
        logger.error(error_msg)
        return error_msg