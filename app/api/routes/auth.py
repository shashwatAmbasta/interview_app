from fastapi import APIRouter, Cookie, Depends, Response

from app.core.config import settings
from app.core.dependencies import cookie_options, current_user
from app.db.database import get_db
from app.schemas.auth import AuthRequest, AuthResponse, UserResponse
from app.services.auth_service import authenticate_user, register_user
from app.services.session_service import session_store

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=AuthResponse)
def register(request: AuthRequest, response: Response, connection=Depends(get_db)) -> AuthResponse:
    user, token = register_user(connection, request, session_store)
    response.set_cookie(settings.cookie_name, token, **cookie_options())
    return AuthResponse(user=user)


@router.post("/login", response_model=AuthResponse)
def login(request: AuthRequest, response: Response, connection=Depends(get_db)) -> AuthResponse:
    user, token = authenticate_user(connection, request, session_store)
    response.set_cookie(settings.cookie_name, token, **cookie_options())
    return AuthResponse(user=user)


@router.post("/logout")
def logout(response: Response, sift_session: str | None = Cookie(default=None)) -> dict[str, bool]:
    if sift_session:
        try:
            session_store.delete(sift_session)
        except Exception:
            pass
    response.delete_cookie(settings.cookie_name, path="/")
    return {"ok": True}


@router.get("/me", response_model=UserResponse)
def me(user=Depends(current_user)) -> UserResponse:
    return UserResponse(id=user["id"], email=user["email"], name=user["name"])
