from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models import UserChat, History
from sqlalchemy.orm import relationship, declarative_base
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()

engine = create_engine(
    DATABASE_URL,
    pool_size     = 5,
    max_overflow  = 10,
    pool_pre_ping = True,   
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    """
    Yield a SQLAlchemy session; close it when the request is done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

