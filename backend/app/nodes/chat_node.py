import json
from typing import Any, Dict
from app.core.model import get_llm
from app.core.prompts import MY_PROMPT
from app.models.model import GlobalState
from langsmith import traceable

@traceable(name="chat_node")
def chat(state: GlobalState) -> GlobalState:
    """
    Executes a chat prompt using the LLM and stores the parsed JSON
    response in state["summary"].
    """

    llm = get_llm()

    prompt = f"{MY_PROMPT}\n\nQUERY: {state.get('query')}"
    response = llm.invoke(prompt)

    raw_content = response.content.strip()
    try:
        res = json.loads(raw_content)
    except json.JSONDecodeError:
        res = {
            "text": raw_content.strip(),
            "type": "text_fallback",
        }
    state["summary"] = res
    return state

