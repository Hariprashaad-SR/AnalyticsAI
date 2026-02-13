from typing import Dict
from collections import defaultdict
import re

def parse_schema(schema_text: str) -> Dict[str, set]:
    schema = defaultdict(set)
    table = None
    for line in schema_text.lower().splitlines():
        line = line.strip()
        if line.startswith("table:"):
            table = line.replace("table:", "").strip()
        elif line.startswith("-") and table:
            schema[table].add(line[1:].split("(")[0].strip())
    return schema


def extract_aliases(sql: str) -> Dict[str, str]:
    """
    returns: alias -> real_table
    """
    pattern = r"(from|join)\s+([a-z_][a-z0-9_]*)\s*(?:as\s+)?([a-z_][a-z0-9_]*)?"
    aliases = {}
    for _, table, alias in re.findall(pattern, sql.lower()):
        aliases[alias or table] = table
    return aliases
