from fastapi import APIRouter, HTTPException, status

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.schemas.auth import UserRegister, UserLogin, TokenPair, RefreshRequest, UserOut

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# Temporary in-memory store — replaced by real persistence in Phase 3
_fake_users_db: dict[str, dict] = {}


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister):
    if payload.email in _fake_users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    _fake_users_db[payload.email] = {
        "email": payload.email,
        "password_hash": hash_password(payload.password),
        "role": "user",
    }
    return UserOut(email=payload.email)


@router.post("/login", response_model=TokenPair)
def login(payload: UserLogin):
    user = _fake_users_db.get(payload.email)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenPair(
        access_token=create_access_token(payload.email),
        refresh_token=create_refresh_token(payload.email),
    )


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest):
    try:
        decoded = decode_token(payload.refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    email = decoded["sub"]
    return TokenPair(
        access_token=create_access_token(email),
        refresh_token=create_refresh_token(email),
    )