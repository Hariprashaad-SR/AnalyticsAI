import pandas as pd
from core.prompts import PANDAS_QUERY_PROMPT
from core.model import get_llm
from helper.get_schema import get_schema_csv
from langsmith import traceable
import pandas as pd

from models.model import GlobalState

@traceable(name='create_query_csv')
def create_query_csv(state: GlobalState) -> GlobalState:
    """
    Uses LLM to generate pandas query code.
    Returns Python code as string.
    """
    llm = get_llm()

    prompt = PANDAS_QUERY_PROMPT.format(
        schema=state['schema'],
        query=state["plan"]['create_query_csv'],
        file=state['uploaded_file']
    )

    response = llm.invoke(prompt)
    state['sql_query'] = response.content.strip()
    return state


@traceable(name='execute_query_csv')
def execute_query_csv(state : GlobalState) -> GlobalState:
    import pandas as pd

    file_path = state['uploaded_file']

    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file type")

    exec_var = {"df": df, "pd" : pd}

    try:
        code = state['sql_query'].replace('```python','').replace('```', '')
        exec(code, exec_var)
    except Exception as e:
        raise RuntimeError(f"Query execution failed: {e}")

    if "result" not in exec_var:
        raise RuntimeError("LLM did not produce a `result` variable")

    state["query_result"] = exec_var["result"]

    return state


