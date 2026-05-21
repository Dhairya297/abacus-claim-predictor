# api/auth/jwt_handler.py
from datetime import datetime, timedelta
from jose import JWTError, jwt

SECRET_KEY  = "abacus-super-secret-jwt-key-2024-change-in-prod"
ALGORITHM   = "HS256"
EXPIRE_MINS = 480  # 8 hours

def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=EXPIRE_MINS)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    """Returns decoded payload or raises JWTError."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])