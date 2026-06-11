"""
auth.py
=======
Authentication and user management for the dashboard.

Endpoints:
    POST /auth/login              — validate credentials, return token + role
    GET  /auth/users              — list all users (admin only)
    POST /auth/users              — add a new user (admin only)
    DELETE /auth/users/{username} — remove a user (admin only, cannot remove admin)

Users are stored in backend/users.json.
Tokens are simple signed JWT tokens using python-jose.

Install:
    pip install python-jose passlib
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header
from jose import JWTError, jwt
from pydantic import BaseModel

# ── Config ────────────────────────────────────────────────────────────────────

SECRET_KEY  = "dashboard_secret_key_marketsof1_2026"   # change in production
ALGORITHM   = "HS256"
TOKEN_EXPIRE_HOURS = 8

USERS_FILE  = Path(__file__).parent / "users.json"

router = APIRouter(prefix="/auth", tags=["Auth"])


# ── Pydantic models ───────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token   : str
    username: str
    role    : str

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    username: str
    role    : str


# ── User store helpers ────────────────────────────────────────────────────────

def _read_users() -> list[dict]:
    """Read users from users.json."""
    if not USERS_FILE.exists():
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def _write_users(users: list[dict]):
    """Write users back to users.json."""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def _find_user(username: str) -> Optional[dict]:
    """Find a user by username (case-insensitive)."""
    users = _read_users()
    for u in users:
        if u["username"].lower() == username.lower():
            return u
    return None


# ── Token helpers ─────────────────────────────────────────────────────────────

def _create_token(username: str, role: str) -> str:
    """Create a JWT token for the user."""
    payload = {
        "sub" : username,
        "role": role,
        "exp" : datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _verify_token(token: str) -> dict:
    """Verify a JWT token and return the payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")


# ── Auth dependency ───────────────────────────────────────────────────────────

def get_current_user(authorization: str = Header(...)) -> dict:
    """
    FastAPI dependency — extracts and verifies the token from
    the Authorization header (Bearer <token>).
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header.")
    token = authorization.split(" ", 1)[1]
    return _verify_token(token)


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """FastAPI dependency — ensures the current user is admin."""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    return current_user


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest):
    """
    Validate credentials and return a JWT token.
    Frontend stores the token in sessionStorage.
    """
    user = _find_user(body.username)

    if not user or user["password"] != body.password:
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    token = _create_token(user["username"], user["role"])

    return {
        "token"   : token,
        "username": user["username"],
        "role"    : user["role"],
    }


@router.get("/users", response_model=list[UserOut])
def list_users(admin: dict = Depends(require_admin)):
    """Return all users. Admin only."""
    users = _read_users()
    return [{"username": u["username"], "role": u["role"]} for u in users]


@router.post("/users", response_model=UserOut)
def add_user(body: UserCreate, admin: dict = Depends(require_admin)):
    """
    Add a new non-admin user. Admin only.
    Username must be unique. New users always get role='user'.
    """
    if not body.username.strip():
        raise HTTPException(status_code=400, detail="Username cannot be empty.")
    if not body.password.strip():
        raise HTTPException(status_code=400, detail="Password cannot be empty.")
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    users = _read_users()

    # Check duplicate
    if any(u["username"].lower() == body.username.lower() for u in users):
        raise HTTPException(status_code=409, detail=f"Username '{body.username}' already exists.")

    new_user = {
        "username": body.username.strip(),
        "password": body.password.strip(),
        "role"    : "user",
    }
    users.append(new_user)
    _write_users(users)

    print(f"[auth] Admin added user: {body.username}")
    return {"username": new_user["username"], "role": new_user["role"]}


@router.delete("/users/{username}")
def delete_user(username: str, admin: dict = Depends(require_admin)):
    """
    Remove a user. Admin only.
    Cannot delete the admin account.
    """
    if username.lower() == "admin":
        raise HTTPException(status_code=400, detail="Cannot delete the admin account.")

    users = _read_users()
    updated = [u for u in users if u["username"].lower() != username.lower()]

    if len(updated) == len(users):
        raise HTTPException(status_code=404, detail=f"User '{username}' not found.")

    _write_users(updated)
    print(f"[auth] Admin deleted user: {username}")
    return {"message": f"User '{username}' deleted successfully."}