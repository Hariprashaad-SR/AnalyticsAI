from app.core.model import get_llm
from langsmith import traceable
from app.models.model import GlobalState
from app.helper.summary_helper import _safe_parse_json, _normalize_summary
from app.core.prompts import SUMMARISE_PROMPT

@traceable(name="summarize_with_llm")
def summarize_with_llm(state: GlobalState) -> GlobalState:
    """
    Uses an LLM to summarize query results into a structured JSON response.
    The output may contain text, a table, follow-up questions, or a combination.
    """

    prompt = _build_summarization_prompt(state)

    llm = get_llm()
    response = llm.invoke(prompt)

    parsed_response = _safe_parse_json(response.content)
    final_summary = _normalize_summary(parsed_response)

    state["summary"] = final_summary
    return state


def _build_summarization_prompt(state: GlobalState) -> str:
    return SUMMARISE_PROMPT.format(plan = state['plan']['summarize_with_llm'], query = state.get('query_result', 'No results found'))

