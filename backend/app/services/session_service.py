import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.model import History, UserChat
from uuid import UUID

def create_session(
    db:        Session,
    user_id:   UUID,
    file_path: str,
    file_type: Optional[str] = None,
    schema:    Optional[str] = None,
) -> str:
    """
    Persist a new chat session row and return its UUID session_id.
    """
    session_id = str(uuid.uuid4())

    chat = UserChat(
        session_id    = session_id,
        user_id       = UUID(user_id),
        uploaded_file = file_path,
        file_type     = file_type,
        schema        = schema,
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return session_id


def get_session(db: Session, session_id: str) -> Optional[Dict[str, Any]]:
    """
    Return a session dict compatible with the original in-memory shape, or None.
    """
    chat = (
        db.query(UserChat)
        .filter(UserChat.session_id == session_id)
        .first()
    )
    if not chat:
        return None

    history_rows = (
        db.query(History)
        .filter(History.session_id == session_id)
        .order_by(History.id.asc())
        .all()
    )

    return {
        "session_id":   chat.session_id,
        "file_path":    chat.uploaded_file,
        "file_type":    chat.file_type,
        "schema":       chat.schema,
        "user_id":      chat.user_id,
        "chat_history": [
            {"query": h.query, "answer": h.answer, "chart_code": h.chart_code, "report": h.report}
            for h in history_rows
        ],
    }


def get_user_sessions(db: Session, user_id: int) -> List[Dict[str, Any]]:
    user_id = uuid.UUID(user_id)
    chats = (
        db.query(UserChat)
        .filter(UserChat.user_id == user_id)
        .order_by(UserChat.created_at.desc())
        .all()
    )
    return [
        {
            "session_id":    c.session_id,
            "uploaded_file": c.uploaded_file,
            "file_type":     c.file_type,
            "created_at":    c.created_at.isoformat() if c.created_at else None,
        }
        for c in chats
    ]


def get_session_history(db: Session, session_id: str) -> List[Dict[str, Any]]:
    """
    Return the full ordered chat history for a session.
    """
    rows = (
        db.query(History)
        .filter(History.session_id == session_id)
        .order_by(History.id.asc())
        .all()
    )
    return [{"query": r.query, "answer": r.answer, "chart_code": r.chart_code, "report": r.report,  "created_at":    r.created_at.isoformat() if r.created_at else None,} for r in rows]


def append_history(
    db:         Session,
    session_id: str,
    query:      str,
    answer:     str,
    chart_code: Optional[str] = None,
    report: Optional[str] = None
) -> History:
    """
    Persist a single (query, answer) turn and return the new History row.
    Replaces direct dict mutation on session["chat_history"].
    """
    entry = History(session_id=session_id, query=query, answer=answer)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry