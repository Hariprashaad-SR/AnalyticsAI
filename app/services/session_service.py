from typing import Dict, Any

sessions: Dict[str, Dict[str, Any]] = {}


def create_session(file_path: str) -> str:
    session_id = f"session_{len(sessions)}"
    sessions[session_id] = {
        "file_path": file_path,
        "chat_history": [],
    }
    return session_id


def get_session(session_id: str) -> Dict[str, Any] | None:
    return sessions.get(session_id)