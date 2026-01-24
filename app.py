from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import shutil
from decimal import Decimal
from graph import graph

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active sessions
sessions: Dict[str, Dict[str, Any]] = {}


class QueryRequest(BaseModel):
    session_id: str
    query: str


class SessionInitRequest(BaseModel):
    file_path: str


def convert_decimals(obj):
    """Convert Decimal objects to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    return obj


# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    with open("static/index.html", "r") as f:
        return f.read()


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle file upload and return session ID"""
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)
        
        # Save uploaded file
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create new session
        session_id = f"session_{len(sessions)}"
        sessions[session_id] = {
            "file_path": file_path,
            "chat_history": []
        }
        
        return {
            "status": "success",
            "session_id": session_id,
            "filename": file.filename,
            "message": "File uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/init-session")
async def init_session(request: SessionInitRequest):
    """Initialize session with a file path (DB connection string or file path)"""
    try:
        session_id = f"session_{len(sessions)}"
        sessions[session_id] = {
            "file_path": request.file_path,
            "chat_history": []
        }
        
        return {
            "status": "success",
            "session_id": session_id,
            "message": "Session initialized successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query")
async def execute_query(request: QueryRequest):
    """Execute a query using the LangGraph workflow"""
    try:
        if request.session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = sessions[request.session_id]
        
        result = graph.invoke({
            'uploaded_file': session['file_path'],
            'query': request.query
        })
        
        result = convert_decimals(result)
        
        # Store in chat history
        session['chat_history'].append({
            "query": request.query,
            "result": result
        })
        
        # Extract only summary and chart_url from the workflow result
        summary = result.get('summary', '')
        chart_url = str(result.get('chart_url', '')).replace('/assets', 'assets')
        
        # If no summary, provide a fallback message
        if not summary:
            summary = "Analysis completed. No summary available."
        
        return {
            "status": "success",
            "summary": summary,
            "chart_url": chart_url if chart_url else None
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error executing query: {error_trace}")
        
        return {
            "status": "error",
            "message": str(e),
            "trace": error_trace
        }


@app.get("/saved_graphs/{filename}")
async def get_chart(filename: str):
    """Return the generated chart from saved_graphs directory"""
    chart_path = f"saved_graphs/{filename}"
    if os.path.exists(chart_path):
        return FileResponse(chart_path, media_type="image/jpeg")
    
    chart_path_png = chart_path.replace('.jpg', '.png')
    if os.path.exists(chart_path_png):
        return FileResponse(chart_path_png, media_type="image/png")
    
    raise HTTPException(status_code=404, detail="Chart not found")


@app.get("/api/sessions/{session_id}/history")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "history": sessions[session_id]['chat_history']
    }


if __name__ == "__main__":
    import uvicorn
    
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    os.makedirs("saved_graphs", exist_ok=True)
    
    print("\n" + "="*60)
    print("DataFlow Analytics Server Starting...")
    print("="*60)
    print("Using LangGraph workflow from main.py")
    print("Server: http://localhost:8000")
    print("Uploads: ./uploads")
    print("Charts: ./saved_graphs")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)