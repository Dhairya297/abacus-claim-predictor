from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from pathlib import Path
import json
import bcrypt

from api.auth.jwt_handler import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

USERS_FILE = Path(__file__).resolve().parents[2] / "config" / "users.json"


def load_users() -> dict:
    if not USERS_FILE.exists():
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users: dict) -> None:
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


class LoginRequest(BaseModel):
    username: str
    password: str


class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)
    confirm_password: str = Field(min_length=6, max_length=128)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    name: str
    username: str


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest):
    users = load_users()
    user = users.get(req.username)

    if not user or not verify_password(req.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )

    token = create_access_token({
        "sub": req.username,
        "role": user["role"],
        "name": user["name"]
    })

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        role=user["role"],
        name=user["name"],
        username=req.username
    )


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(req: SignupRequest):
    if req.password != req.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match."
        )

    users = load_users()

    if req.username in users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists."
        )

    users[req.username] = {
        "password": hash_password(req.password),
        "role": "billing_analyst",
        "name": req.username.replace("_", " ").title()
    }

    save_users(users)

    token = create_access_token({
        "sub": req.username,
        "role": users[req.username]["role"],
        "name": users[req.username]["name"]
    })

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        role=users[req.username]["role"],
        name=users[req.username]["name"],
        username=req.username
    )


@router.get("/me")
def me():
    return {"status": "ok"}