import json
from typing import List
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from langsmith import traceable
from app.core.prompts import SQL_PROMPT, SQL_PROMPT2, VERIFICATION_PROMPT
from app.core.model import get_llm
from app.helper.get_schema import columns_dict_to_text
from app.helper.parse_schema import parse_schema, extract_aliases
from app.helper.validation_helper import _extract_sql_from_response, _validate_tables, _validate_columns, _validate_bare_columns
from app.models.model import GlobalState

@traceable(name="create_sql_query")
def create_sql_query(state: GlobalState) -> GlobalState:
    """
    Generate an SQL query using an LLM based on the application state.
    """

    llm = get_llm()

    prompt_template = (
        SQL_PROMPT2 if state.get("file_type") == "sqlDB" else SQL_PROMPT
    )

    system_prompt = prompt_template.format(
        schema=state.get("schema"),
        query=state["plan"]["create_sql_query"],
        db_type=state.get("file_type"),
        error_message=state.get("errors", "N/A"),
    )

    response = llm.invoke(system_prompt)
    sql_query = _extract_sql_from_response(response.content)

    state["sql_query"] = sql_query
    state["check_count"] = state.get("check_count", 0) + 1
    state["errors"] = []

    return state


@traceable(name="verify_sql_query")
def verify_sql_query(state: GlobalState) -> GlobalState:
    """
    Verify SQL correctness using schema inspection and LLM validation.
    """

    errors: List[str] = []

    # Skip verification for SQL DBs or after max retries
    if state.get("file_type") == "sqlDB" or state.get("check_count") == 2:
        state["verified_sql"] = True
        return state

    sql = state.get("sql_query", "").strip()
    question = state["plan"]["verify_sql_query"]
    schema_text = state.get("schema")

    if isinstance(schema_text, dict):
        schema_text = columns_dict_to_text(schema_text)
        state["schema"] = schema_text

    if not sql or not schema_text:
        state["verified_sql"] = False
        state["errors"] = ["SQL query or schema is missing"]
        return state

    schema = parse_schema(schema_text)
    alias_map = extract_aliases(sql)
    used_tables = set(alias_map.values())

    _validate_tables(used_tables, schema, errors)
    _validate_columns(sql, alias_map, schema, used_tables, errors)
    _llm_verify_sql(sql, question, schema_text, state.get("file_type"), errors)

    state["verified_sql"] = len(errors) == 0
    state["errors"] = errors

    return state


@traceable(name="execute_sql_query")
def execute_sql_query(state: GlobalState) -> GlobalState:
    """
    Execute a SELECT-only SQL query using SQLAlchemy.
    """

    sql = state.get("sql_query", "")
    connection_string = state.get("uploaded_file")

    if not connection_string:
        state["errors"] = "Database connection string missing"
        return state

    try:
        engine = create_engine(connection_string)

        with engine.connect() as connection:
            result = connection.execute(text(sql))
            rows = result.fetchall()
            columns = result.keys()

            state["query_result"] = [
                dict(zip(columns, row)) for row in rows
            ]

        return state

    except SQLAlchemyError as exc:
        state["errors"] = str(exc)
        return state


@traceable(name="end_node")
def end_node(state: GlobalState) -> GlobalState:
    """
    Fallback node when execution is not possible.
    """
    state["query_result"] = "No result can be generated for the query"
    state["summary"] = "This action cannot be performed"
    return state

# ------------------------------------------------

def _llm_verify_sql(
    sql: str,
    question: str,
    schema_text: str,
    db_type: str,
    errors: List[str],
) -> None:
    try:
        llm = get_llm()
        prompt = VERIFICATION_PROMPT.format(
            question=question,
            sql=sql,
            schema_text=schema_text,
            db_type=db_type,
        )

        result = json.loads(llm.invoke(prompt).content)

        if not result.get("valid", True):
            errors.extend(
                f"LLM: {issue}" for issue in result.get("issues", [])
            )

    except Exception as exc:
        errors.append(f"LLM validation failed: {exc}")

