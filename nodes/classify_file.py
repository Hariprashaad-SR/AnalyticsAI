from core.regex import POSTGRES_REGEX, GENERIC_SQL_REGEX
from langsmith import traceable
from helper.get_schema import get_schema, get_schema_csv
from models.model import GlobalState

@traceable(name='classify_file')
def classify_file(state : GlobalState) -> GlobalState:
    """
    Classifies uploaded_file deterministically WITHOUT using an LLM.
    """
    uploaded = state.get("uploaded_file")

    if not uploaded:
        state["file_type"] = "not_supported"
        return state

    filename = ""

    if isinstance(uploaded, str):
        identifier = uploaded.strip()

        if POSTGRES_REGEX.match(identifier):
            state["file_type"] = "postgresDB"
            return state

        if GENERIC_SQL_REGEX.match(identifier):
            state["file_type"] = "sqlDB"
            return state

        filename = identifier

    elif isinstance(uploaded, dict):
        filename = uploaded.get("name", "")

    else:
        state["file_type"] = "not_supported"
        return state

    ext = filename.split(".")[-1].lower() if "." in filename else ""

    EXTENSION_MAP = {
        "csv": "csv",
        "json": "json",
        "txt": "text",
        "log": "text",
        "pdf": "pdf",
        "xls": "excel",
        "xlsx": "excel",
        "sql": "sqlDB"
    }
    if ext in EXTENSION_MAP:
        state["file_type"] = EXTENSION_MAP[ext]
        return state

    state["file_type"] = "not_supported"
    return state
