from fastapi import APIRouter, HTTPException
from app.models.model import SessionInitRequest
from app.services.session_service import create_session
from app.graphs.main_graph import graph


router = APIRouter(prefix="/api", tags=["Session"])


@router.post("/init-session")
async def init_session(request: SessionInitRequest):
    try:
        session_id = create_session(request.file_path)

        graph.invoke({
            "uploaded_file": request.file_path,
            "query": None,
            "session_id": session_id,
        })

        return {
            "status": "success",
            "session_id": session_id,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))