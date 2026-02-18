import base64
import json
from urllib.parse import urlencode
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app import service
from app.config   import settings
from app.database import get_db
from app.schemas  import LoginRequest, SignupRequest, TokenResponse, UserOut
from fastapi.encoders import jsonable_encoder
from dotenv import load_dotenv
import os

load_dotenv()

router  = APIRouter(prefix="/api/auth", tags=["auth"])
_bearer = HTTPBearer()
logger = logging.getLogger("auth")
logging.basicConfig(level=logging.INFO)

GOOGLE_AUTH_URL = os.getenv('GOOGLE_AUTH_URL')


def current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> int:
    uid = service.verify_access_token(credentials.credentials).get("user_id")
    if uid is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return uid


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register with email + password",
)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    if service.get_user_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )
    user  = service.create_user(db, payload.name, payload.email, payload.password)
    token = service.create_access_token({"user_id" : str(user.id)})
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email + password",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = service.get_user_by_email(db, payload.email)

    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password.",
    )

    if not user or not user.hashed_password:
        raise invalid
    if not service.verify_password(payload.password, user.hashed_password):
        raise invalid
    # if not user.is_active:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="This account has been deactivated.",
    #     )

    token = service.create_access_token({"user_id" : str(user.id)})
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.get("/google", summary="Start Google OAuth flow")
def google_login():
    logger.info("Starting Google OAuth flow")

    if not settings.google_client_id:
        logger.error("GOOGLE_CLIENT_ID missing in settings")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured.",
        )

    logger.debug(f"Redirect URI: {settings.google_redirect_uri}")
    logger.debug(f"Client ID: {settings.google_client_id}")

    params = urlencode({
        "client_id":     settings.google_client_id,
        "redirect_uri":  settings.google_redirect_uri,
        "response_type": "code",
        "scope":         "openid email profile",
        "access_type":   "offline",
        "prompt":        "select_account",
    })

    redirect_url = f"{GOOGLE_AUTH_URL}?{params}"
    logger.info(f"Redirecting to Google: {redirect_url}")

    return RedirectResponse(url=redirect_url)


@router.get("/google/callback", summary="Google OAuth callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    logger.info("Received Google OAuth callback")

    if not code:
        logger.error("No code received from Google")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authorization code.",
        )

    logger.debug(f"Authorization code: {code}")

    try:
        google_info = await service.google_exchange_code(code)
        logger.info(f"Google user info received: {google_info}")
    except Exception as exc:
        logger.exception("Google exchange failed")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google OAuth failed: {str(exc)}",
        )

    try:
        user = service.upsert_google_user(db, google_info)
        logger.info(f"User upserted with ID: {str(user.id)}")
    except Exception:
        logger.exception("Database error during Google user upsert")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save Google user.",
        )

    token = service.create_access_token({"user_id" : str(user.id)})
    logger.info(f"JWT created for user {str(user.id)}")


    user_b64 = base64.b64encode(
        json.dumps(jsonable_encoder(UserOut.model_validate(user))).encode()
    ).decode()
    redirect_url = (
        f"{settings.frontend_origin}"
        f"?token={token}"
        f"&user={user_b64}"
    )

    logger.info(f"Redirecting back to frontend: {redirect_url}")

    return RedirectResponse(url=redirect_url)


@router.get("/me", response_model=UserOut, summary="Get current user")
def me(
    uid: int         = Depends(current_user_id),
    db: Session      = Depends(get_db),
):
    user = service.get_user_by_id(db, uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return UserOut.model_validate(user)
