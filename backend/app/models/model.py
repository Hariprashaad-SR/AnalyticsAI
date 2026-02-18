from typing import TypedDict, Dict, List
import json
from pydantic import BaseModel
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, Text, String, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship, declarative_base
import uuid
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()


def _now():
    return datetime.now(timezone.utc)


class GlobalState(TypedDict):
    uploaded_file:str
    file_type:str
    query:str
    sql_query:str
    query_result:str
    py_code:str
    summary:json
    schema: str
    plan : Dict
    verified_sql: bool
    errors : List
    chart_url : str
    file : str
    report : str
    summaries : List
    report_plan : List
    check_count : int
    current_step : int
    session_id: str
    extracted:json


class QueryRequest(BaseModel):
    session_id: str
    query: str


class SessionInitRequest(BaseModel):
    file_path: str



class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    pic = Column(Text, nullable=True)
    hashed_password = Column(Text, nullable=True)
    google_id = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    # relationships
    sessions = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    userchats = relationship(
        "UserChat",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserSession(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    access_token = Column(Text, unique=True, nullable=False, index=True)
    refresh_token = Column(Text, unique=True, nullable=True)
    expiry_time = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    user = relationship("User", back_populates="sessions")


class UserChat(Base):
    __tablename__ = "userchats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    session_id = Column(Text, unique=True, nullable=False, index=True)
    uploaded_file = Column(Text, nullable=True)
    file_type = Column(Text, nullable=True)
    schema = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=_now,
        onupdate=_now,
    )

    user = relationship("User", back_populates="userchats")
    history = relationship(
        "History",
        back_populates="chat",
        cascade="all, delete-orphan",
    )


class History(Base):
    __tablename__ = "history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    session_id = Column(
        Text,
        ForeignKey("userchats.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    query = Column(Text, nullable=True)
    answer = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    chart_code = Column(Text, nullable=True)
    report = Column(Text, nullable=True)


    chat = relationship("UserChat", back_populates="history")
