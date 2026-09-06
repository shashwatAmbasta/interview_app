import sqlite3
from datetime import datetime, timezone

from fastapi import HTTPException

from app.core.security import create_access_token, verify_password
from app.db.repositories import create_user, find_user_by_email
from app.schemas.auth import AuthRequest, UserResponse
from app.services.session_service import SessionStore


def register_user(connection: sqlite3.Connection, request: AuthRequest, sessions: SessionStore) -> tuple[UserResponse, str]:
    name = request.name.strip() or request.email.split("@")[0].title()
    try:
        user = create_user(connection, request.email, name, request.password, datetime.now(timezone.utc).isoformat())
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="An account with that email already exists")
    return _start_session(user, sessions)


def authenticate_user(connection: sqlite3.Connection, request: AuthRequest, sessions: SessionStore) -> tuple[UserResponse, str]:
    record = find_user_by_email(connection, request.email)
    if not record or not verify_password(request.password, record["password_hash"]):
        raise HTTPException(status_code=401, detail="Email or password is incorrect")
    return _start_session(record, sessions)


def _start_session(user: sqlite3.Row, sessions: SessionStore) -> tuple[UserResponse, str]:
    sessions.require_available()
    token = create_access_token(user["id"], user["email"])
    sessions.create(token, user["id"])
    return UserResponse(id=user["id"], email=user["email"], name=user["name"]), token
