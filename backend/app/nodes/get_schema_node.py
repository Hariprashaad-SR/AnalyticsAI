from langsmith import traceable
from app.core.logger import AppLogger
from app.helper.get_schema import get_schema
from app.utils.local_db import save_session_file_state
from app.models.model import GlobalState

logger = AppLogger.get_logger(__name__)

@traceable(name="get_dbschema")
def get_dbschema(state: GlobalState) -> GlobalState:
    """
    Retrieve database schema for the uploaded file and persist it
    in the session state.
    """

    logger.info("Retrieving database schema")

    uploaded_file = state.get("uploaded_file")
    if not uploaded_file:
        logger.warning("No uploaded file found; skipping schema retrieval")
        return state

    try:
        state["schema"] = get_schema(uploaded_file)
        save_session_file_state(state)
        logger.info("Database schema retrieved successfully")

    except Exception as e:
        logger.exception("Failed to retrieve database schema")
        state["errors"] = str(e)

    return state
