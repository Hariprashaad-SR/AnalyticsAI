from typing import Any, Dict, List
import json
import re

def _extract_sql_from_response(content: str) -> str:
    """
    Extract SQL from an LLM response, handling fenced and unfenced outputs.
    """
    if "```sql" in content.lower():
        try:
            return (
                content.split("```")[1]
                .replace("sql", "", 1)
                .strip()
                .replace("\n", " ")
            )
        except IndexError:
            pass

    return content.replace("\n", " ").strip()


def _validate_tables(
    used_tables: set,
    schema: Dict[str, Any],
    errors: List[str],
) -> None:
    for table in used_tables:
        if table not in schema:
            errors.append(f"Table '{table}' not found in schema")


def _validate_columns(
    sql: str,
    alias_map: Dict[str, str],
    schema: Dict[str, Any],
    used_tables: set,
    errors: List[str],
) -> None:
    col_refs = re.findall(
        r"([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)",
        sql.lower(),
    )

    for alias, column in col_refs:
        if alias not in alias_map:
            errors.append(f"Unknown table alias '{alias}'")
            continue

        table = alias_map[alias]
        if column not in schema.get(table, []):
            errors.append(f"Column '{column}' not in table '{table}'")

    _validate_bare_columns(sql, schema, used_tables, errors)


def _validate_bare_columns(
    sql: str,
    schema: Dict[str, Any],
    used_tables: set,
    errors: List[str],
) -> None:
    matches = re.findall(
        r"select\s+(.*?)\s+from",
        sql.lower(),
        re.DOTALL,
    )

    if not matches:
        return

    for expr in matches[0].split(","):
        expr = re.sub(r"\s+as\s+.*", "", expr.strip())

        if "." in expr or "(" in expr or expr == "*":
            continue

        candidate_tables = [
            table for table in used_tables if expr in schema.get(table, [])
        ]

        if not candidate_tables:
            errors.append(f"Bare column '{expr}' not found in used tables")
        elif len(candidate_tables) > 1:
            errors.append(f"Ambiguous bare column '{expr}'")

