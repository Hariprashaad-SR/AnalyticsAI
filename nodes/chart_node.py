import os
import shutil
import matplotlib.pyplot as plt
from langsmith import traceable
from models.model import GlobalState
from core.prompts import CHART_GEN_PROMPT 
from core.model import get_llm

@traceable(name='create_charts')
def create_charts(state : GlobalState) -> GlobalState:
    """
    Uses an LLM to generate Python matplotlib code
    for a detailed chart based on the data.
    """
    if state['plan'].get('execute_chart_code', '') == '':
        return state
    
    llm = get_llm() 

    prompt = CHART_GEN_PROMPT.format(
        user_query=state.get('plan')['create_charts'],
        data=state.get('query_result'),
    )

    response = llm.invoke(prompt)
    state['py_code'] = response.content.strip()

    return state



@traceable(name='execute_chart_code')
def execute_chart_code(state : GlobalState) -> GlobalState:
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
