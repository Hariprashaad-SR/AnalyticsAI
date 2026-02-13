import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse


router = APIRouter(tags=["Assets"])


@router.get("/saved_graphs/{filename}")
async def get_chart(filename: str):
    base_path = f"saved_graphs/{filename}"

    if os.path.exists(base_path):
        return FileResponse(base_path)

    png_path = base_path.replace(".jpg", ".png")
    if os.path.exists(png_path):
        return FileResponse(png_path)

    raise HTTPException(status_code=404, detail="Chart not found")