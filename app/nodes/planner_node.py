from typing import Any, Dict
import json
from langsmith import traceable
from colorama import Fore, Style 
from app.core.model import get_llm
from app.core.prompts import PLANNER_PROMPT, SQL_QUERY_PROMPT
from app.utils.local_db import load_last_two_messages
from app.helper.plan_helper import _load_schema, _parse_planner_response, _generate_sql_plan
from app.models.model import GlobalState

@traceable(name="planning_agent")
def planning_agent(state: GlobalState) -> GlobalState:
    """
    Generates an execution plan for the user's query using an LLM.
    Also prepares an initial SQL generation instruction.
    """

    llm = get_llm()

    # schema = _load_schema(
    #     uploaded_file=state.get("uploaded_file"),
    #     file_type=state.get("file_type"),
    # )
    schema = state.get("schema", "No schema available")

    conversation_history = load_last_two_messages(state["session_id"])

    planner_prompt = PLANNER_PROMPT.format(
        query=state["query"],
        file_type=state["file_type"],
        schema=schema,
        history=conversation_history,
    )

    response = llm.invoke(planner_prompt)
    plan = _parse_planner_response(response.content)

    plan["create_sql_query"] = _generate_sql_plan(
        llm=llm,
        query=state["query"],
        history=conversation_history,
        schema=state.get("schema"),
    )

    state["plan"] = plan
    state["check_count"] = 0

    return state
