from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from pathlib import Path
from passlib.context import CryptContext
import json

from api.auth.jwt_handler import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

# ─────────────────────────────────────────────
# Password hashing
# ─────────────────────────────────────────────
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# ─────────────────────────────────────────────
# Load users from JSON
# ─────────────────────────────────────────────
USERS_FILE = Path("config/users.json")

with open(USERS_FILE, "r") as f:
    USERS = json.load(f)

# ─────────────────────────────────────────────
# Request / Response Models
# ─────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    name: str

# ─────────────────────────────────────────────
# Login Route
# ─────────────────────────────────────────────
@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):

    user = USERS.get(req.username)

    # User not found
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )

    # Verify bcrypt password
    valid_password = pwd_context.verify(
        req.password,
        user["password"]
    )

    if not valid_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )

    # Create JWT token
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

# ─────────────────────────────────────────────
# Optional token check endpoint
# ─────────────────────────────────────────────
@router.get("/me")
def me():
    return {"status": "ok"}