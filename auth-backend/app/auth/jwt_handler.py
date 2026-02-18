from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.config import settings
import uuid

SECRET_KEY = settings.secret_key
# REFRESH_SECRET_KEY = settings.JWT_REFRESH_KEY
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 60
ACCESS_TOKEN_EXPIRE_SECONDS = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict):
    to_encode = data
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire, "type": "access", "jti": jti})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

# def create_refresh_token(data: int, expire_delta:timedelta|None = None):
#     to_encode = data
#     expire = expire_delta or (datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
#     jti = str(uuid.uuid4())
#     to_encode.update({"exp": expire, "type": "refresh", "jti": jti})
#     token = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
#     return token


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None

# def verify_refresh_token(token: str):
#     try:
#         payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
#         if payload.get("type") != "refresh":
#             return None
#         return payload
#     except JWTError:
#         return None

