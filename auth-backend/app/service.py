from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID
import httpx
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models import User, UserSession
from app.config import settings
from app.auth.hash import hash_password, verify_password
from app.auth.jwt_handler import create_access_token, verify_access_token
import os
from dotenv import load_dotenv

load_dotenv()

def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(
        User.email == email.lower().strip()
    ).first()


def create_user(db: Session, name: str, email: str, password: str) -> User:
    user = User(
        name = name.strip(),
        email = email.lower().strip(),
        hashed_password = hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_session(
    db:            Session,
    user_id:       UUID,
    access_token:  str,
    expiry_time:   datetime,
    refresh_token: Optional[str] = None,
) -> UserSession:
    """Persist a new access/refresh token pair for a user."""
    session = UserSession(
        user_id       = user_id,
        access_token  = access_token,
        refresh_token = refresh_token,
        expiry_time   = expiry_time,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session_by_access_token(db: Session, token: str) -> Optional[UserSession]:
    return db.query(UserSession).filter(
        UserSession.access_token == token
    ).first()


def delete_session(db: Session, token: str) -> None:
    """Revoke a session by deleting its token row."""
    db.query(UserSession).filter(
        UserSession.access_token == token
    ).delete(synchronize_session=False)
    db.commit()


GOOGLE_TOKEN_URL    = os.getenv('GOOGLE_TOKEN_URL')
GOOGLE_USERINFO_URL = os.getenv('GOOGLE_USERINFO_URL')


async def google_exchange_code(code: str) -> dict:
    """Trade an OAuth authorisation code for Google user-info."""
    async with httpx.AsyncClient(timeout=10) as client:
        token_res = await client.post(GOOGLE_TOKEN_URL, data={
            "code":          code,
            "client_id":     settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri":  settings.google_redirect_uri,
            "grant_type":    "authorization_code",
        })
        token_res.raise_for_status()
        tokens = token_res.json()

        info_res = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        info_res.raise_for_status()
        return info_res.json()


def upsert_google_user(db: Session, info: dict) -> User:
    google_id = info["id"]
    email     = info["email"].lower()

    user = db.query(User).filter(User.google_id == google_id).first()
    if user:
        user.pic = info.get("picture")
        db.commit()
        db.refresh(user)
        return user

    user = get_user_by_email(db, email)
    if user:
        user.google_id = google_id
        user.pic = info.get("picture")
        db.commit()
        db.refresh(user)
        return user

    user = User(
        name = info.get("name", email.split("@")[0]),
        email = email,
        google_id = google_id,
        pic = info.get("picture"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user