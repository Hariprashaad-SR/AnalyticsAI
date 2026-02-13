import json
from typing import Dict, Any
from langsmith import traceable
from app.core.model import get_llm
from app.core.prompts import CHART_GEN_PROMPT
from app.helper.chart_helper import _sanitize_code, _execute_plotly_code
from app.models.model import GlobalState

@traceable(name="create_charts")
def create_charts(state: GlobalState) -> GlobalState:
    """
    Uses an LLM to generate Plotly Python code for chart creation.
    The generated code is stored in state["py_code"].
    """

    if not state.get("plan", {}).get("execute_chart_code"):
        return state

    llm = get_llm()

    prompt = CHART_GEN_PROMPT.format(
        user_query=state["plan"]["create_charts"],
        data=state.get("query_result"),
    )

    response = llm.invoke(prompt)

    state["py_code"] = response.content.strip()
    return state


@traceable(name="execute_chart_code")
def execute_chart_code(state: GlobalState) -> GlobalState:
    """
    Executes LLM-generated Plotly code in a restricted environment.
    Expects the code to produce a Plotly figure named `fig`.
    """

    if not state.get("plan", {}).get("execute_chart_code"):
        return state

    raw_code = state.get("py_code", "")
    code = _sanitize_code(raw_code)

    try:
        fig = _execute_plotly_code(
            code=code,
            sql_result=state.get("query_result"),
        )

        state.update(
            {
                "chart_url": fig.to_json(),
                "chart_engine": "plotly",
            }
        )

    except Exception as e:
        state["errors"] = f"Chart execution failed: {e}"

    return state


