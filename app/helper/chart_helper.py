from typing import Any, Dict

def _sanitize_code(code: str) -> str:
    """
    Remove markdown fences from LLM-generated Python code.
    """
    return (
        code.replace("```python", "")
        .replace("```", "")
        .strip()
    )


def _execute_plotly_code(code: str, sql_result: Any):
    """
    Execute Plotly code in a restricted execution environment.
    The executed code MUST define a variable named `fig`.
    """
    import plotly.express as px
    import plotly.graph_objects as go
    import pandas as pd

    exec_env: Dict[str, Any] = {
        "px": px,
        "go": go,
        "pd": pd,
        "sql_result": sql_result,
    }

    exec(code, exec_env)

    fig = exec_env.get("fig")
    if fig is None:
        raise RuntimeError("Plotly figure `fig` was not created")

    return fig
