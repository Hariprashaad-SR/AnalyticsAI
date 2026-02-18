from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from app.models.model import SessionInitRequest
from app.services.session_service import create_session, get_session_history, get_user_sessions
from app.graphs.main_graph import graph
from app.utils.local_db import get_db
from app.auth.oauth_bearer import get_current_user

router = APIRouter(prefix="/api", tags=["Session"])


@router.post("/init-session")
async def init_session(request: SessionInitRequest, db=Depends(get_db), user=Depends(get_current_user)):
    try:
        session_id = create_session(db, user['user_id'], request.file_path)

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
        print(exc)
        raise HTTPException(status_code=500, detail=str(exc))
    
@router.get("/sessions")
def list_sessions(db=Depends(get_db), user=Depends(get_current_user)):
    return {"sessions": get_user_sessions(db, user['user_id'])}

@router.get("/sessions/{session_id}/history")
def session_history(session_id: str, db=Depends(get_db)):
    return {"history": get_session_history(db, session_id)}