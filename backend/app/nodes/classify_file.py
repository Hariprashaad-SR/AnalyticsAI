from typing import Dict
from langsmith import traceable
from app.core.logger import AppLogger
from app.core.regex import POSTGRES_REGEX, GENERIC_SQL_REGEX
from app.models.model import GlobalState

logger = AppLogger.get_logger(__name__)

EXTENSION_MAP: Dict[str, str] = {
    "csv": "csv",
    "json": "json",
    "txt": "text",
    "log": "text",
    "pdf": "pdf",
    "xls": "excel",
    "xlsx": "excel",
    "sql": "sqlDB",
    "png": "image",
    "jpg": "image",
    "jpeg": "image",
    "webp": "image",
    "bmp": "image",
    "tiff": "image",
}

@traceable(name="classify_file")
def classify_file(state: GlobalState) -> GlobalState:
    """
    Classifies the uploaded file or connection string deterministically
    without using an LLM.
    """

    logger.info("Entering classify_file node")

    uploaded = state.get("uploaded_file")
    if not uploaded:
        state["file_type"] = "not_supported"
        return state

    filename = _extract_filename(uploaded)

    if isinstance(uploaded, str):
        identifier = uploaded.strip()

        if POSTGRES_REGEX.match(identifier):
            state["file_type"] = "postgresDB"
            logger.info("Detected PostgreSQL connection string")
            return state

        if GENERIC_SQL_REGEX.match(identifier):
            state["file_type"] = "sqlDB"
            logger.info("Detected generic SQL connection string")
            return state

    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    state["file_type"] = EXTENSION_MAP.get(extension, "not_supported")

    logger.info(f"Detected file type: {state['file_type']}")
    logger.info("Exiting classify_file node")

    return state


def _extract_filename(uploaded: object) -> str:
    """
    Extract filename from supported uploaded_file formats.
    """
    if isinstance(uploaded, str):
        return uploaded.strip()

    if isinstance(uploaded, dict):
        return uploaded.get("name", "")

    return ""

