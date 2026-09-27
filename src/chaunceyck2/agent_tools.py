from langchain_core.tools import tool
import sqlite3
from chaunceyck2.constants import *

def _connect() -> sqlite3.Connection:
    # Open read-only so the agent can never modify the knowledge base.
    return sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)

@tool('run_sql', description="Run a query on the CK2 database to provide and answer")
def run_sql(query: str) -> str:

    #TODO: Add logic for SQLite Query
    
    return "run_sql test"
