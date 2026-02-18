from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.params import Depends
from app.services.file_service import save_uploaded_file
from app.services.session_service import create_session
from app.graphs.main_graph import graph
from app.utils.local_db import get_db
from app.auth.oauth_bearer import get_current_user


router = APIRouter(prefix="/api", tags=["Upload"])


@router.post("/upload")
async def upload_file(db=Depends(get_db), user=Depends(get_current_user),file: UploadFile = File(...)):
    try:
        file_path = save_uploaded_file(file)
        session_id = create_session(db, user['user_id'],file_path)

        graph.invoke({
            "uploaded_file": file_path,
            "query": None,
            "session_id": session_id,
        })

        return {
            "status": "success",
            "session_id": session_id,
            "filename": file.filename,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))