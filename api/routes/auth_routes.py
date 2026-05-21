from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from pathlib import Path
import json
import bcrypt

from api.auth.jwt_handler import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

USERS_FILE = Path(__file__).resolve().parents[2] / "config" / "users.json"

with open(USERS_FILE, "r") as f:
    USERS = json.load(f)

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    name: str

@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    user = USERS.get(req.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )

    password_ok = bcrypt.checkpw(
        req.password.encode("utf-8"),
        user["password"].encode("utf-8")
    )

    if not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )

    token = create_access_token({
        "sub": req.username,
        "role": user["role"],
        "name": user["name"]
    })

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        role=user["role"],
        name=user["name"]
    )

@router.get("/me")
def me():
    return {"status": "ok"}