from app.graphs.main_graph import graph
from app.utils.local_db import save_history
from app.utils.serialization import convert_decimals


def run_query(
    session_id: str,
    file_path: str,
    query: str,
) -> dict:
    result = graph.invoke({
        "uploaded_file": file_path,
        "query": query,
        "session_id": session_id,
    })

    result = convert_decimals(result)
    save_history(session_id, query, str(result.get("summary", "")), str(result.get("chart_url", "")), str(result.get("report", "")))

    return result