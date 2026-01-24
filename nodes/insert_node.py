import pandas as pd
import sqlite3
import os
from pathlib import Path
from langsmith import traceable

from models.model import GlobalState

@traceable(name='file_to_sqlite')
def file_to_sqlite(state : GlobalState) -> GlobalState:
    if state['file_type'] not in ['csv', 'excel']:
        return state
    file_path = Path(state['uploaded_file'])
    table_name = 'data'

    sqlite_db_path = file_path.with_suffix(".db")

    if file_path.suffix.lower() == ".csv":
        df = pd.read_csv(file_path)
    elif file_path.suffix.lower() in [".xls", ".xlsx"]:
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Only CSV or Excel files are supported")

    conn = sqlite3.connect(sqlite_db_path)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()

    connection_string = f"sqlite:///{os.path.abspath(sqlite_db_path)}"
    state['uploaded_file'] = connection_string
    state['file_type'] = 'sqlDB'
    return state
