from typing import Dict, Any
import json
from app.core.prompts import SQL_QUERY_PROMPT
from app.helper.get_schema import get_schema, get_schema_csv

def _load_schema(uploaded_file: str, file_type: str) -> Any:
    """
    Load schema depending on file type.
    """
    if file_type in {"csv", "excel"}:
        return get_schema_csv(uploaded_file)
    return get_schema(uploaded_file)


def _parse_planner_response(raw_content: str) -> Dict[str, Any]:
    """
    Parse planner JSON output from the LLM.
    """
    try:
        return json.loads(raw_content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Planner failed to return valid JSON"
        ) from exc


def _generate_sql_plan(
    llm,
    query: str,
    history: str,
    schema: Any,
) -> str:
    """
    Generate the SQL query instruction using a secondary prompt.
    """
    response = llm.invoke(
        SQL_QUERY_PROMPT.format(
            question=query,
            history=history,
            schema=schema,
        )
    )
    return response.content.strip()
