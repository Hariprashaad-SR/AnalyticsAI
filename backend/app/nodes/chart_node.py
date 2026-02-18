import json
import os
import shutil
from typing import Dict, Any
from langsmith import traceable
from app.core.model import get_llm
from app.core.prompts import CHART_GEN_PROMPT, CHART_GEN_PROMPT2
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



@traceable(name='create_charts_report')
def create_charts_report(state : GlobalState) -> GlobalState:
    """
    Uses an LLM to generate Python matplotlib code
    for a detailed chart based on the data.
    """
    if state['plan'].get('execute_chart_code', '') == '':
        return state
    
    llm = get_llm() 

    prompt = CHART_GEN_PROMPT2.format(
        user_query=state.get('plan')['create_charts'],
        data=state.get('query_result'),
    )

    response = llm.invoke(prompt)
    state['py_code'] = response.content.strip()

    return state



@traceable(name='execute_chart_code_report')
def execute_chart_code_report(state : GlobalState) -> GlobalState:
    if state['plan'].get('execute_chart_code', '') == '':
        return state
    
    code = state['py_code']
    code = code.replace('```python', '').replace('```', '')

    forbidden = ["open(", "__", "eval", "exec", "os.", "sys."]
    # if any(f in code for f in forbidden):
    #     raise RuntimeError("Unsafe code detected in chart generation")
    exec_env = {}

    try:
        exec(code, exec_env)

        src = exec_env.get("output_path")
        dst_dir = "./saved_graphs"
        dst = os.path.join(dst_dir, os.path.basename(src))

        os.makedirs(dst_dir, exist_ok=True)
        shutil.move(src, dst)
        state["chart_url"] = f"/saved_graphs/{src}"

        print("Chart created:", state["chart_url"])
        return state

    except Exception as e:
        print(f"Chart execution failed: {e}")
        return state
