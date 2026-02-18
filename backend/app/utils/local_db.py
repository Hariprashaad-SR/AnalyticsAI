import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.models.model import UserChat, History

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:HariSR035@localhost:5432/analyticsAI"
)

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


@contextmanager
def db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db() -> Generator[Session, None, None]:
    """
    Yield a SQLAlchemy session; close it when the request is done.
    Usage in FastAPI:
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_session_file_state(state: dict) -> UserChat:
    """
    Upsert a UserChat row for the given session_id.
    """
    with db_session() as db:

        chat = (
            db.query(UserChat)
            .filter(UserChat.session_id == state["session_id"])
            .first()
        )

        if chat:
            chat.uploaded_file = state.get("uploaded_file", chat.uploaded_file)
            chat.file_type = state.get("file_type", chat.file_type)
            chat.schema = state.get("schema", chat.schema)
        else:
            chat = UserChat(
                session_id=state["session_id"],
                user_id=1,
                uploaded_file=state.get("uploaded_file"),
                file_type=state.get("file_type"),
                schema=state.get("schema"),
            )
            db.add(chat)

        db.flush()
        return chat


def load_session_file_state(session_id: str) -> dict:
    with db_session() as db:

        chat = (
            db.query(UserChat)
            .filter(UserChat.session_id == session_id)
            .first()
        )

        if not chat:
            return {}

        return {
            "session_id": chat.session_id,
            "user_id": chat.user_id,
            "uploaded_file": chat.uploaded_file,
            "file_type": chat.file_type,
            "schema": chat.schema,
        }


def save_history(session_id: str, query: str, answer: str, chart_code: str = None, report: str = None) -> History:
    print(f"Saving history for session_id={session_id}, query={query}, answer={answer}, chart_code={chart_code}, report={report}")
    with db_session() as db:

        entry = History(
            session_id=session_id,
            query=query,
            answer=answer,
            chart_code = chart_code, 
            report = report
        )

        db.add(entry)
        db.flush()
        return entry


def load_last_n_messages(session_id: str, n: int = 2) -> list[dict]:
    with db_session() as db:

        rows = (
            db.query(History)
            .filter(History.session_id == session_id)
            .order_by(History.id.desc())
            .limit(n)
            .all()
        )

        rows.reverse()

        return [
            {"query": r.query, "answer": r.answer}
            for r in rows
        ]


def load_last_two_messages(session_id: str) -> list[dict]:
    return load_last_n_messages(session_id, n=2)