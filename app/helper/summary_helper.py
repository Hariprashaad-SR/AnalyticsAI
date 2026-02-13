import json
from typing import Any, Dict, List

def _safe_parse_json(raw_content: str) -> Dict[str, Any]:
    """
    Attempts to parse JSON from the LLM response.
    Falls back to plain text if parsing fails.
    """
    try:
        return json.loads(raw_content)
    except json.JSONDecodeError:
        return {
            "text": raw_content.strip(),
            "type": "text_fallback"
        }


def _normalize_summary(summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates and normalizes the LLM output into a predictable structure.
    """

    normalized: Dict[str, Any] = {}

    _extract_text(summary, normalized)
    _extract_table(summary, normalized)
    _extract_followups(summary, normalized)

    normalized["type"] = _infer_summary_type(normalized)

    if "text" not in normalized and "table" not in normalized:
        normalized["text"] = "No useful summary could be generated."
        normalized["type"] = "text"

    return normalized


def _extract_text(source: Dict[str, Any], target: Dict[str, Any]) -> None:
    if isinstance(source.get("text"), str):
        target["text"] = source["text"].strip()
    elif isinstance(source.get("content"), str):
        target["text"] = source["content"].strip()


def _extract_table(source: Dict[str, Any], target: Dict[str, Any]) -> None:
    table = source.get("table")

    if not isinstance(table, dict):
        return

    columns = table.get("columns")
    rows = table.get("rows")

    if (
        isinstance(columns, list)
        and columns
        and isinstance(rows, list)
        and all(isinstance(row, list) for row in rows)
    ):
        target["table"] = {
            "columns": columns,
            "rows": rows
        }


def _extract_followups(source: Dict[str, Any], target: Dict[str, Any]) -> None:
    followups = source.get("followups", [])

    if not isinstance(followups, list):
        target["followups"] = []
        return

    cleaned: List[str] = []
    for question in followups:
        if isinstance(question, str):
            question = question.strip()
            if 3 <= len(question) <= 120:
                cleaned.append(question)

    target["followups"] = cleaned[:4]


def _infer_summary_type(summary: Dict[str, Any]) -> str:
    if "text" in summary and "table" in summary:
        return "hybrid"
    if "table" in summary:
        return "table"
    if "text" in summary:
        return "text"
    return "text"
