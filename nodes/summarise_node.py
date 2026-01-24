from core.model import get_llm
from langsmith import traceable

from models.model import GlobalState

@traceable(name='summarize_with_llm')
def summarize_with_llm(state : GlobalState) -> GlobalState:
    """
    Generate a user-friendly summary using an LLM.

    Args:
        llm: An LLM object with an `invoke` method.
        text (str): The text or data to summarize.
        format_type (str): 'paragraph', 'table', or 'auto' (default).
                           - 'paragraph': returns a textual summary.
                           - 'table': returns a table format (markdown style).
                           - 'auto': decides based on content type.

    Returns:
        str: Formatted summary.
    """
    prompt = f"""
    Summarize the following information clearly for a user in simple english
    Provide the concise answer for the user query. Dont add any extra information.
    Give the result in a markdown format
   
    Query:
    {state['plan']['summarize_with_llm']}

    Result:
    {state.get('query_result', 'No results found')}

    Format:
    Depending on the content
    """

    llm = get_llm()
    response = llm.invoke(prompt)
    summary = response.content.strip()
    state['summary'] = summary
    return state








