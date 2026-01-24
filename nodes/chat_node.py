
from core.model import get_llm
from core.prompts import MY_PROMPT
from models.model import GlobalState


def chat(state : GlobalState) -> GlobalState:
    llm = get_llm()
    query_prompt = f"\n\nQUERY : {state['query']}"
    
    res = llm.invoke(MY_PROMPT + query_prompt).content
    state['summary'] = res.content
    return state
