# api/auth/jwt_handler.py
import boto3
import json
from datetime import datetime, timedelta
from jose import JWTError, jwt
from functools import lru_cache

ALGORITHM   = "HS256"
EXPIRE_MINS = 480  # 8 hours

@lru_cache(maxsize=1)
def get_secret_key() -> str:
    client = boto3.client("secretsmanager", region_name="us-east-1")
    response = client.get_secret_value(SecretId="abacus/jwt")
    secret = json.loads(response["SecretString"])
    return secret["JWT_SECRET_KEY"]

def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=EXPIRE_MINS)
    return jwt.encode(payload, get_secret_key(), algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    """Returns decoded payload or raises JWTError."""
    return jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])