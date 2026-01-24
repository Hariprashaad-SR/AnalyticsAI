from typing import TypedDict, Dict, List

class GlobalState(TypedDict):
    uploaded_file:str
    file_type:str
    query:str
    sql_query:str
    query_result:str
    py_code:str
    summary:str
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

