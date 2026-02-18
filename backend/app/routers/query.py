from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from app.models.model import QueryRequest
from app.services.session_service import get_session
from app.services.query_service import run_query
from app.utils.local_db import get_db


router = APIRouter(prefix="/api", tags=["Query"])


@router.post("/query")
async def execute_query(request: QueryRequest, db=Depends(get_db)):
    session = get_session(db, request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    result = run_query(
        request.session_id,
        session["file_path"],
        request.query,
    )

    session["chat_history"].append({
        "query": request.query,
        "result": result
    })


    return {
        "status": "success",
        "summary": result.get("summary", "Report generated successfully"),
        "chart_url": result.get("chart_url"),
        "report" : str(result.get("report", ""))
    }