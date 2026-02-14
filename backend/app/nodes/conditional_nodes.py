from typing import Literal
from app.core.model import get_llm
from app.core.prompts import CLASSIFY_PROMPT
from app.graphs.chart_graph import chart_graph
from app.graphs.report_graph import report_graph
from app.graphs.sql_graph import sql_graph
from app.utils.local_db import load_last_two_messages
from app.models.model import GlobalState

def sql_node(state: GlobalState) -> GlobalState:
    return sql_graph.invoke(state)


def chart_node(state: GlobalState) -> GlobalState:
    return chart_graph.invoke(state)


def report_node(state: GlobalState) -> GlobalState:
    return report_graph.invoke(state)


def router(state: GlobalState) -> Literal["generate_report", "sql_node"]:
    """
    Route queries to report generation or SQL execution.
    """
    query = state.get("query", "").lower()

    if any(keyword in query for keyword in {"report", "detailed"}):
        return "generate_report"

    return "sql_node"


def router2(state: GlobalState) -> Literal["create_charts", "summarize_with_llm"]:
    """
    Route post-SQL results to chart creation or summarization.
    """
    query = state.get("query", "").lower()

    if any(keyword in query for keyword in {"chart", "graph"}):
        return "create_charts"

    return "summarize_with_llm"


def is_sql(state: GlobalState) -> Literal["insert_node", "get_schema"]:
    """
    Decide whether to insert data or fetch schema.
    """
    if state.get("file_type") in {"csv", "excel", "image"}:
        return "insert_node"

    return "get_schema"


def is_chart(state: GlobalState) -> Literal["chart_node", "summarize"]:
    """
    Decide whether chart generation is required.
    """
    if state.get("plan", {}).get("execute_chart_code"):
        return "chart_node"

    return "summarize"


def is_valid(state: GlobalState) -> Literal["end", "decision"]:
    """
    Validate SQL execution outcome.
    """
    if state.get("sql_query") == "This action cannot be done":
        return "end"

    return "decision"


def check_intent(state: GlobalState) -> str:
    """
    Classify user intent using an LLM with conversation context.
    """
    history = load_last_two_messages(state["session_id"])

    prompt = (
        f"{CLASSIFY_PROMPT}\n\n"
        f"query = {state.get('query')}\n\n"
        f"History = {history}"
    )

    response = get_llm().invoke(prompt)
    return response.content.strip()
