from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.file_service import save_uploaded_file
from app.services.session_service import create_session
from app.graphs.main_graph import graph


router = APIRouter(prefix="/api", tags=["Upload"])


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = save_uploaded_file(file)
        session_id = create_session(file_path)

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