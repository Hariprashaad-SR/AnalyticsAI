from typing import TypedDict, Dict, List
import json
from pydantic import BaseModel


class GlobalState(TypedDict):
    uploaded_file:str
    file_type:str
    query:str
    sql_query:str
    query_result:str
    py_code:str
    summary:json
    schema: str
    plan : Dict
    verified_sql: bool
    errors : List
    chart_url : str
    file : str
    report : str
    summaries : List
    report_plan : List
    check_count : int
    current_step : int
    session_id: str
    extracted:json


class QueryRequest(BaseModel):
    session_id: str
    query: str


class SessionInitRequest(BaseModel):
    file_path: str