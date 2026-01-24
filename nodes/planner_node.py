from colorama import Fore, Style
from core.model import get_llm
from helper.get_schema import get_schema, get_schema_csv
from core.prompts import PLANNER_PROMPT, SQL_QUERY_PROMPT
import json
from langsmith import traceable
from models.model import GlobalState

@traceable(name='planning_agent')
def planning_agent(state: GlobalState) -> GlobalState:
    llm = get_llm()
    schema = get_schema_csv(state['uploaded_file']) if state['file_type'] in  ['csv', 'excel'] else get_schema(state['uploaded_file'])
    prompt = PLANNER_PROMPT.format(
        query=state["query"],
        file_type=state["file_type"],
        schema = schema
    )

    response = llm.invoke(prompt)

    try:
        plan = json.loads(response.content)
        plan['create_sql_query'] =  llm.invoke(SQL_QUERY_PROMPT.format(question = state['query'], schema = state['schema'])).content
    except Exception:
        raise RuntimeError("Planner failed to return valid plan")

    state["plan"] = plan
    state['check_count'] = 0

    print(Fore.CYAN + "Execution Plan:")
    for i, step in enumerate(plan):
        print(f"  Step {i+1}: {step}")
    print(Style.RESET_ALL)
    return state

