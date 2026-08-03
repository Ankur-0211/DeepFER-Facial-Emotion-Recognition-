from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import select

from app.core.security import decode_token
from app.db.session import get_db
from app.db.models import User


def get_current_user(
    authorization: str = Header(None),
    db: DBSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.removeprefix("Bearer ")
    try:
        decoded = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if decoded.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")
    user = db.scalar(select(User).where(User.email == decoded["sub"]))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user