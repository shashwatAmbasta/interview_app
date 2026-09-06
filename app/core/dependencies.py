import sqlite3

from fastapi import Cookie, Depends, HTTPException, status

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.database import get_db
from app.db.repositories import find_user_by_id
from app.services.session_service import session_store


def current_user(
    sift_session: str | None = Cookie(default=None),
    connection: sqlite3.Connection = Depends(get_db),
) -> sqlite3.Row:
    if not sift_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in to continue")
    try:
        payload = decode_access_token(sift_session)
        user_id = int(payload["sub"])
    except (Exception,):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Your session has expired")
    try:
        if not session_store.exists(sift_session):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Your session has expired")
    except Exception as error:
        if isinstance(error, HTTPException):
            raise
        raise HTTPException(status_code=503, detail="Redis session store is unavailable") from error
    user = find_user_by_id(connection, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return user


def cookie_options() -> dict:
    return {"httponly": True, "secure": settings.cookie_secure, "samesite": "lax", "max_age": settings.session_ttl_seconds, "path": "/"}
