from core.prompts import SQL_PROMPT, VERIFICATION_PROMPT, SQL_PROMPT2
from core.model import get_llm
from helper.get_schema import get_schema, columns_dict_to_text
from typing import Dict, Any, List
from helper.parse_schema import parse_schema, extract_aliases
import re
import json
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from langsmith import traceable

from models.model import GlobalState

@traceable(name='create_sql_query')
def create_sql_query(state : GlobalState) -> GlobalState:
    """
    Generate an SQL query using an LLM based on the current application state.
    """
    llm = get_llm()
    prompt = SQL_PROMPT
    if state['file_type'] == 'sqlDB':
        prompt = SQL_PROMPT2
        
    system_prompt = prompt.format(schema = state['schema'], query = state['plan']['create_sql_query'], db_type = state['file_type'], error_message = state.get('errors', 'N/A'))
    response = llm.invoke(system_prompt)
    state["sql_query"] = response.content.replace('\n', ' ').split('```')[1].strip()[4:] if '```sql' in response.content else response.content.replace('\n', ' ')
    state['check_count'] = state['check_count'] + 1
    state['errors'] = []
    print(state['check_count'], '\n')
    return state


@traceable(name='verify_sql_query')
def verify_sql_query(state: GlobalState) -> GlobalState:
    errors: List[str] = []
    if state['file_type'] == 'sqlDB' or state['check_count'] == 2:
        state['verified_sql'] = True
        return state

    sql = state.get("sql_query", "").strip()
    question = state.get("plan", "")['verify_sql_query']
    schema_text = state.get("schema", "")
    if isinstance(schema_text, dict):
        schema_text  = columns_dict_to_text(schema_text)
        state['schema'] = schema_text

    if not sql or not schema_text:
        state["verified_sql"] = False
        state["errors"] = ["SQL or schema missing"]
        return state

    schema = parse_schema(str(schema_text))
    alias_map = extract_aliases(sql)
    used_tables = set(alias_map.values())


    for table in used_tables:
        if table not in schema:
            errors.append(f"Table '{table}' not found in schema")


    col_refs = re.findall(r"([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)", sql.lower())

    for alias, col in col_refs:
        if alias not in alias_map:
            errors.append(f"Unknown table alias '{alias}'")
            continue
        table = alias_map[alias]
        if col not in schema[table]:
            errors.append(f"Column '{col}' not in table '{table}'")

  
    bare_cols = re.findall(
        r"select\s+(.*?)\s+from", sql.lower(), re.DOTALL
    )

    if bare_cols:
        for expr in bare_cols[0].split(","):
            expr = re.sub(r"\s+as\s+.*", "", expr.strip())
            if "." in expr or "(" in expr or expr in {"*"}:
                continue
            matches = [t for t in used_tables if expr in schema[t]]
            if not matches:
                errors.append(f"Bare column '{expr}' not found in used tables")
            elif len(matches) > 1:
                errors.append(f"Ambiguous bare column '{expr}'")

    try:
        llm = get_llm()
        prompt = VERIFICATION_PROMPT.format(question = question, sql = sql, schema_text = schema_text, db_type = state['file_type'])
        result = json.loads(llm.invoke(prompt).content)
        if not result.get("valid", True):
            errors.extend([f"LLM: {i}" for i in result.get("issues", [])])
    except Exception as e:
        errors.append(f"LLM validation failed: {str(e)}")

    state["verified_sql"] = len(errors) == 0
    state["errors"] = errors
    return state


@traceable(name='execute_sql_query')
def execute_sql_query(state : GlobalState) -> GlobalState:
    """
    Execute a SELECT-only SQL query using a SQLAlchemy connection string.

    Required in state:
        state['db_connection'] : str  (SQLAlchemy connection string)
        state['sql_query']     : str

    Sets in state:
        state['query_result'] : list[dict]
        state['errors']        : str (only if failure)

    Returns:
        state
    """
    sql = state.get("sql_query", "")
    conn_str = state.get("uploaded_file")

    # ---------- SAFETY: SELECT ONLY ----------
    # if not sql.lower().startswith("select"):
    #     state["errors"] = "Only SELECT queries are allowed"
    #     return state

    if not conn_str:
        state["errors"] = "Database connection string missing"
        return state
    try:
        engine = create_engine(conn_str)
        with engine.connect() as connection:
            result = connection.execute(text(sql))

            # Convert rows → list of dicts
            rows = result.fetchall()
            columns = result.keys()
            state["query_result"] = [
                dict(zip(columns, row)) for row in rows
            ]

        return state

    except SQLAlchemyError as e:
        state["errors"] = str(e)
        return state


@traceable(name='end_node')
def end_node(state : GlobalState) -> GlobalState:
    state['query_result'] = "No result can be generated for the query"
    state['summary'] = 'This action cannot be performed'
    return state

