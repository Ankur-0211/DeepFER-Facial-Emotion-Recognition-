from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import select

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.db.session import get_db
from app.db.models import User
from app.schemas.auth import UserRegister, UserLogin, TokenPair, RefreshRequest, UserOut

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: DBSession = Depends(get_db)):
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut(email=user.email, role=user.role)


@router.post("/login", response_model=TokenPair)
def login(payload: UserLogin, db: DBSession = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenPair(
        access_token=create_access_token(user.email),
        refresh_token=create_refresh_token(user.email),
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